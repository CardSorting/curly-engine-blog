import logging
from typing import Dict, Any, List, Tuple
from .models import OperationTransform
from diff_match_patch import diff_match_patch
import hashlib

logger = logging.getLogger(__name__)


class OperationalTransform:
    """
    Operational Transformation utility for conflict-free collaborative editing
    Implements industry-standard OT algorithms using diff-match-patch
    """

    def __init__(self):
        self.dmp = diff_match_patch()
        # Configure diff-match-patch for better performance
        self.dmp.Diff_Timeout = 1.0  # 1 second timeout
        self.dmp.Diff_EditCost = 4    # Make edits more expensive than matches

    @staticmethod
    def create_operation_from_diff(old_text: str, new_text: str, position_offset: int = 0) -> List[Dict[str, Any]]:
        """
        Create fine-grained operations from text diff using diff-match-patch
        Returns a list of atomic operations (insert/delete)
        """
        if old_text == new_text:
            return []

        ot = OperationalTransform()
        diffs = ot.dmp.diff_main(old_text, new_text)

        # Clean up diffs for better performance
        ot.dmp.diff_cleanupSemantic(diffs)
        ot.dmp.diff_cleanupEfficiency(diffs)

        operations = []
        current_position = position_offset

        for diff_type, text in diffs:
            if diff_type == 0:  # EQUAL - advance position
                current_position += len(text)
            elif diff_type == 1:  # INSERT
                operations.append({
                    'type': 'insert',
                    'position': current_position,
                    'text': text,
                    'timestamp': ot._get_timestamp()
                })
                current_position += len(text)
            elif diff_type == -1:  # DELETE
                operations.append({
                    'type': 'delete',
                    'position': current_position,
                    'length': len(text),
                    'timestamp': ot._get_timestamp()
                })
                # Don't advance position for deletes

        return operations

    @staticmethod
    def create_single_operation(old_content: str, new_content: str) -> Dict[str, Any]:
        """
        Create a single comprehensive operation for simple cases
        Used when we need a single operation rather than multiple atomic ones
        """
        if old_content == new_content:
            return None

        # Use diff-match-patch to find the differences
        ot = OperationalTransform()
        diffs = ot.dmp.diff_main(old_content, new_content)
        ot.dmp.diff_cleanupSemantic(diffs)

        # If it's a simple case (single diff), create appropriate operation
        if len(diffs) == 1:
            diff_type, text = diffs[0]
            if diff_type == 1:  # Pure insert
                return {
                    'type': 'insert',
                    'position': 0,
                    'text': text,
                    'timestamp': ot._get_timestamp()
                }
            elif diff_type == -1:  # Pure delete
                return {
                    'type': 'delete',
                    'position': 0,
                    'length': len(text),
                    'timestamp': ot._get_timestamp()
                }
        elif len(diffs) == 3 and diffs[0][0] == 0 and diffs[2][0] == 0:
            # Simple replacement: EQUAL + DELETE/INSERT + EQUAL
            _, prefix_text = diffs[0]
            diff_type, changed_text = diffs[1]
            _, suffix_text = diffs[2]

            if diff_type == -1:  # DELETE then INSERT (replacement)
                # Find the actual replacement in new_content
                prefix_len = len(prefix_text)
                old_changed_len = len(changed_text)
                replacement_end = prefix_len + len(new_content) - len(old_content) + old_changed_len

                new_text = new_content[prefix_len:replacement_end]
                return {
                    'type': 'replace',
                    'position': prefix_len,
                    'old_text': changed_text,
                    'new_text': new_text,
                    'timestamp': ot._get_timestamp()
                }

        # Fallback: use replace operation for complex changes
        return {
            'type': 'replace',
            'position': 0,
            'old_text': old_content,
            'new_text': new_content,
            'timestamp': ot._get_timestamp()
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp for operations"""
        from django.utils import timezone
        return timezone.now().isoformat()

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute hash of content for versioning"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def transform_operation(operation: Dict[str, Any], concurrent_operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an operation against a concurrent operation
        Returns the transformed operation
        """
        op_type = operation.get('type')
        concurrent_type = concurrent_operation.get('type')

        if op_type == 'insert' and concurrent_type == 'insert':
            return OperationalTransform._transform_insert_insert(operation, concurrent_operation)
        elif op_type == 'insert' and concurrent_type == 'delete':
            return OperationalTransform._transform_insert_delete(operation, concurrent_operation)
        elif op_type == 'delete' and concurrent_type == 'insert':
            return OperationalTransform._transform_delete_insert(operation, concurrent_operation)
        elif op_type == 'delete' and concurrent_type == 'delete':
            return OperationalTransform._transform_delete_delete(operation, concurrent_operation)

        # No transformation needed for other cases
        return operation

    @staticmethod
    def _transform_insert_insert(op1: Dict[str, Any], op2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform two insert operations
        IT rule: If two inserts at the same position, the later one shifts right
        """
        pos1 = op1.get('position', 0)
        pos2 = op2.get('position', 0)
        text1 = op1.get('text', '')
        text2 = op2.get('text', '')

        if pos1 < pos2:
            # Insert 1 comes before Insert 2, no change
            return op1
        elif pos1 > pos2:
            # Insert 1 comes after Insert 2, shift position
            return {
                **op1,
                'position': pos1 + len(text2)
            }
        else:  # pos1 == pos2
            # Same position: this operation should come after the concurrent one
            return {
                **op1,
                'position': pos1 + len(text2)
            }

    @staticmethod
    def _transform_insert_delete(op1: Dict[str, Any], op2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform insert operation against delete operation
        """
        insert_pos = op1.get('position', 0)
        insert_text = op1.get('text', '')
        delete_pos = op2.get('position', 0)
        delete_length = op2.get('length', 0)

        delete_end = delete_pos + delete_length

        if insert_pos <= delete_pos:
            # Insert before delete, no change
            return op1
        elif insert_pos < delete_end:
            # Insert within deleted range, adjust to keep relative position
            return {
                **op1,
                'position': delete_pos
            }
        else:
            # Insert after delete, adjust position
            return {
                **op1,
                'position': insert_pos - delete_length
            }

    @staticmethod
    def _transform_delete_insert(op1: Dict[str, Any], op2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform delete operation against insert operation
        """
        delete_pos = op1.get('position', 0)
        delete_length = op1.get('length', 0)
        insert_pos = op2.get('position', 0)
        insert_text = op2.get('text', '')

        if insert_pos <= delete_pos:
            # Insert before delete, shift delete position
            return {
                **op1,
                'position': delete_pos + len(insert_text)
            }
        elif insert_pos < delete_pos + delete_length:
            # Insert within delete range, adjust delete parameters
            return {
                **op1,
                'position': insert_pos,
                'length': delete_length + len(insert_text)
            }
        else:
            # Insert after delete, no change
            return op1

    @staticmethod
    def _transform_delete_delete(op1: Dict[str, Any], op2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform delete operation against another delete operation
        """
        pos1 = op1.get('position', 0)
        len1 = op1.get('length', 0)
        pos2 = op2.get('position', 0)
        len2 = op2.get('length', 0)

        end1 = pos1 + len1
        end2 = pos2 + len2

        if pos1 < pos2:
            if end1 <= pos2:
                # Delete 1 completely before Delete 2, no change
                return op1
            else:
                # Overlapping deletes, merge ranges
                return {
                    'type': 'delete',
                    'position': pos1,
                    'length': max(end1, end2) - pos1
                }
        else:
            if end2 <= pos1:
                # Delete 2 completely before Delete 1, shift Delete 1
                return {
                    **op1,
                    'position': pos1 - len2
                }
            else:
                # Overlapping deletes starting at different points
                new_pos = pos2
                new_len = max(end1, end2) - pos2
                return {
                    'type': 'delete',
                    'position': new_pos,
                    'length': new_len
                }

    @staticmethod
    def apply_operation_to_text(operation: Dict[str, Any], text: str) -> str:
        """
        Apply a single operation to text
        Returns the modified text
        """
        op_type = operation.get('type')
        position = operation.get('position', 0)

        if op_type == 'insert':
            text_to_insert = operation.get('text', '')
            return text[:position] + text_to_insert + text[position:]
        elif op_type == 'delete':
            length = operation.get('length', 0)
            return text[:position] + text[position + length:]
        elif op_type == 'replace':
            old_text = operation.get('old_text', '')
            new_text = operation.get('new_text', '')
            return text.replace(old_text, new_text, 1)

        return text

    @staticmethod
    def apply_operation_to_title(operation: Dict[str, Any], title: str) -> str:
        """
        Apply operation to title (subset of text operations)
        """
        op_type = operation.get('type')

        # Only allow insert/delete operations on title
        if op_type in ['insert', 'delete']:
            return OperationalTransform.apply_operation_to_text(operation, title)

        return title

    @staticmethod
    def validate_operation(operation: Dict[str, Any], text_length: int = None) -> bool:
        """
        Validate operation parameters
        Returns True if operation is valid
        """
        op_type = operation.get('type')
        position = operation.get('position', 0)

        if op_type not in ['insert', 'delete', 'replace']:
            return False

        if position < 0:
            return False

        if op_type == 'insert':
            if 'text' not in operation:
                return False
        elif op_type == 'delete':
            length = operation.get('length', 0)
            if length <= 0:
                return False
            if text_length is not None and position + length > text_length:
                return False
        elif op_type == 'replace':
            if 'old_text' not in operation or 'new_text' not in operation:
                return False

        return True

    @staticmethod
    def compose_operations(op1: Dict[str, Any], op2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compose two operations into a sequence
        Returns a list of operations that achieve the same result
        """
        # For simplicity, return both operations
        # In a full implementation, this would optimize the operation sequence
        return [op1, op2]

    @staticmethod
    def invert_operation(operation: Dict[str, Any], original_text: str = None) -> Dict[str, Any]:
        """
        Create the inverse of an operation (for undo)
        """
        op_type = operation.get('type')

        if op_type == 'insert':
            position = operation.get('position', 0)
            text = operation.get('text', '')
            return {
                'type': 'delete',
                'position': position,
                'length': len(text)
            }
        elif op_type == 'delete':
            position = operation.get('position', 0)
            length = operation.get('length', 0)
            # We need the original text to recreate the insert
            if original_text:
                deleted_text = original_text[position:position + length]
                return {
                    'type': 'insert',
                    'position': position,
                    'text': deleted_text
                }
        elif op_type == 'replace':
            position = operation.get('position', 0)
            old_text = operation.get('old_text', '')
            new_text = operation.get('new_text', '')
            return {
                'type': 'replace',
                'position': position,
                'old_text': new_text,
                'new_text': old_text
            }

        return operation

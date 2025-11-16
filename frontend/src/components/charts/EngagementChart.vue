<template>
  <div class="relative h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import {
  Chart,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  type ChartConfiguration,
} from 'chart.js'

Chart.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

interface Props {
  data: Array<{ metric: string; value: number }>
}

const props = defineProps<Props>()
const chartCanvas = ref<HTMLCanvasElement>()
let chartInstance: Chart | null = null

const createChart = () => {
  if (!chartCanvas.value) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  const config: ChartConfiguration = {
    type: 'bar',
    data: {
      labels: props.data.map(d => d.metric),
      datasets: [
        {
          label: 'Value',
          data: props.data.map(d => d.value),
          backgroundColor: [
            'rgba(34, 197, 94, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(251, 146, 60, 0.8)',
            'rgba(168, 85, 247, 0.8)',
          ],
          borderColor: [
            'rgb(34, 197, 94)',
            'rgb(59, 130, 246)',
            'rgb(251, 146, 60)',
            'rgb(168, 85, 247)',
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const metric = context.label || ''
              const parsedValue = context.parsed.y
              if (parsedValue === null) return `${metric}: N/A`
              
              let value = parsedValue.toString()
              
              // Format based on metric type
              if (metric.includes('Time')) {
                value = `${value} min`
              } else if (metric.includes('Rate')) {
                value = `${value}%`
              } else {
                value = parseInt(value).toLocaleString()
              }
              
              return `${metric}: ${value}`
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
          ticks: {
            maxRotation: 45,
            minRotation: 45,
          },
        },
        y: {
          beginAtZero: true,
        },
      },
    },
  }

  if (chartInstance) {
    chartInstance.destroy()
  }
  chartInstance = new Chart(ctx, config)
}

watch(() => props.data, () => {
  nextTick(() => {
    createChart()
  })
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    createChart()
  })
})
</script>

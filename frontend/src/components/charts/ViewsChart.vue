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
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  type ChartConfiguration,
} from 'chart.js'
import 'chartjs-adapter-date-fns'

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

interface Props {
  data: Array<{ date: string; views: number }>
}

const props = defineProps<Props>()
const chartCanvas = ref<HTMLCanvasElement>()
let chartInstance: Chart | null = null

const createChart = () => {
  if (!chartCanvas.value) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  const config: ChartConfiguration = {
    type: 'line',
    data: {
      labels: props.data.map(d => d.date),
      datasets: [
        {
          label: 'Views',
          data: props.data.map(d => d.views),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true,
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
            title: (context) => {
              if (context[0]) {
                const date = new Date(context[0].label)
                return date.toLocaleDateString()
              }
              return ''
            },
            label: (context) => {
              return `Views: ${context.parsed.y}`
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
            maxTicksLimit: 6,
            callback: (value, index) => {
              if (index !== undefined && index < props.data.length && props.data[index]) {
                const date = new Date(props.data[index].date)
                return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
              }
              return ''
            },
          },
        },
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => value.toLocaleString(),
          },
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

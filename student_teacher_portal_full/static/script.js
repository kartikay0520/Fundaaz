document.addEventListener('DOMContentLoaded', function() {
  const showGraphBtn = document.getElementById('showGraphBtn');
  const graphModal = document.getElementById('graphModal');
  const closeModal = document.getElementById('closeModal');
  const graphForm = document.getElementById('graphForm');
  const progressChart = document.getElementById('progressChart');
  let chartInstance = null;

  if (showGraphBtn) {
    showGraphBtn.onclick = () => {
      graphModal.style.display = 'flex';
    };
  }
  if (closeModal) {
    closeModal.onclick = () => {
      graphModal.style.display = 'none';
      if (chartInstance) chartInstance.destroy();
    };
  }
  if (graphModal) {
    graphModal.onclick = function(e) {
      if (e.target === graphModal) {
        graphModal.style.display = 'none';
        if (chartInstance) chartInstance.destroy();
      }
    };
  }

  if (graphForm) {
    graphForm.onsubmit = function(e) {
      e.preventDefault();
      const student = document.getElementById('studentSelect').value;
      const startDate = document.getElementById('startDate').value;
      const endDate = document.getElementById('endDate').value;
      fetch(`/get_progress?student=${encodeURIComponent(student)}&start_date=${startDate}&end_date=${endDate}`)
        .then(res => res.json())
        .then(data => {
          if (chartInstance) chartInstance.destroy();
          const labels = data.map(d => d.date + ' (' + d.subject + ')');
          const percentages = data.map(d => d.percentage);
          chartInstance = new Chart(progressChart, {
            type: 'line',
            data: {
              labels: labels,
              datasets: [{
                label: 'Test Percentage',
                data: percentages,
                borderColor: '#4f46e5',
                backgroundColor: 'rgba(79,70,229,0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 5,
                pointBackgroundColor: '#06b6d4'
              }]
            },
            options: {
              scales: {
                y: { beginAtZero: true, max: 100 }
              }
            }
          });
        });
    };
  }
});
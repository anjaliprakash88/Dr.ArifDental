const ctx = document.getElementById('lineChart');

new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    datasets: [{
      label: 'view',
      data: [12, 19, 3, 5, 2, 3, 6, 7, 8, 9, 20, 15],
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});
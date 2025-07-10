document.addEventListener("DOMContentLoaded", () => {
  // ---------------- LINE CHART (Orders vs Shipments) ----------------
  const chartDataElement = document.getElementById("dashboard-data");
  if (chartDataElement) {
    const chartData = JSON.parse(chartDataElement.textContent);

    const ctx = document
      .getElementById("ordersShipmentsChart")
      .getContext("2d");

    new Chart(ctx, {
      type: "line",
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: "Orders",
            data: chartData.orders,
            borderColor: "rgb(75, 192, 192)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            fill: false,
            tension: 0.3,
          },
          {
            label: "Shipments",
            data: chartData.shipments,
            borderColor: "rgb(153, 102, 255)",
            backgroundColor: "rgba(153, 102, 255, 0.2)",
            fill: false,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0,
            },
          },
        },
      },
    });
  }

  // ===== Category Chart (Doughnut) =====
  const categoryDataScript = document.getElementById("category-data-script");

  if (categoryDataScript) {
    try {
      const categoryChartData = JSON.parse(categoryDataScript.textContent);
      const ctx = document.getElementById("categoryChart");

      if (ctx) {
        new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: categoryChartData.labels,
            datasets: [
              {
                label: "Products per Category",
                data: categoryChartData.data,
                backgroundColor: [
                  "#6366F1",
                  "#F59E0B",
                  "#10B981",
                  "#EF4444",
                  "#8B5CF6",
                  "#3B82F6",
                  "#F43F5E",
                  "#22D3EE",
                  "#14B8A6",
                ],
                borderColor: "#fff",
                borderWidth: 2,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: "right",
                labels: {
                  color: "#4B5563",
                  font: {
                    size: 14,
                  },
                },
              },
              title: {
                display: false,
              },
            },
          },
        });
      } else {
        console.warn("No canvas found for categoryChart");
      }
    } catch (error) {
      console.error("Error parsing category chart data:", error);
    }
  }
});

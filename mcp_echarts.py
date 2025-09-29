from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("ChartMCP", port=8001)


@mcp.tool()
def bar_chart(title: str, x: list[str], y: list[float], x_label: str = "", y_label: str = "") -> str:
    """
    根据输入的数据生成柱状图配置（返回 JSON 字符串，可直接传给 ECharts）
    """
    option = {
        "chart_type": "bar",
        "title": title,
        "x": x,
        "y": y,
        "x_label": x_label,
        "y_label": y_label
    }
    return json.dumps(option, ensure_ascii=False)


@mcp.tool()
def line_chart(title: str, x: list[str], y: list[float], x_label: str = "", y_label: str = "") -> str:
    """
    生成折线图配置
    """
    option = {
        "chart_type": "line",
        "title": title,
        "x": x,
        "y": y,
        "x_label": x_label,
        "y_label": y_label
    }
    return json.dumps(option, ensure_ascii=False)


@mcp.tool()
def pie_chart(title: str, data: list[dict]) -> str:
    """
    生成饼图配置
    data 格式: [{"name": "手机", "value": 100}, {"name": "电脑", "value": 200}]
    """
    option = {
        "chart_type": "pie",
        "title": title,
        "data": data
    }
    return json.dumps(option, ensure_ascii=False)


@mcp.tool()
def scatter_chart(title: str, points: list[list[float]], x_label: str = "", y_label: str = "") -> str:
    """
    生成散点图配置
    points 格式: [[170, 65], [180, 75], ...]
    """
    option = {
        "chart_type": "scatter",
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "points": points
    }
    return json.dumps(option, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    """
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <title>一句话生成图表示例</title>
  <!-- 引入 ECharts CDN -->
  <script src="https://cdn.jsdelivr.net/npm/echarts/dist/echarts.min.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    #chart { width: 600px; height: 400px; margin-top: 20px; }
  </style>
</head>
<body>
  <h2>一句话生成图表示例</h2>
  <input id="inputText" type="text" placeholder="请输入一句话，例如：展示一周销售额" style="width:300px;" />
  <button onclick="fetchData()">生成图表</button>

  <div id="chart"></div>

  <script>
    // 模拟接口
    function mockApi(userInput) {
      // 实际上这里会调用后端+大模型，这里先返回固定 JSON
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
  "chart_type": "bar",
  "title": "随机数据柱状图",
  "x": ["类别A", "类别B", "类别C", "类别D", "类别E"],
  "y": [45.0, 78.0, 23.0, 65.0, 89.0],
  "x_label": "分类",
  "y_label": "数值"
});
        }, 500); // 模拟网络延迟
      });
    }

    async function fetchData() {
      const userInput = document.getElementById("inputText").value;
      const data = await mockApi(userInput);

      // 渲染图表
      const chartDom = document.getElementById('chart');
      const myChart = echarts.init(chartDom);
      const option = {
        title: { text: data.title },
        tooltip: {},
        xAxis: { type: "category", data: data.x, name: data.x_label },
        yAxis: { type: "value", name: data.y_label },
        series: [{ type: data.chart_type, data: data.y }]
      };
      myChart.setOption(option);
    }
  </script>
</body>
</html>
    """
(async function () {
  const casePicker = document.querySelector("#audit-case");
  const modelPicker = document.querySelector("#audit-model");
  const output = document.querySelector("#audit-views");
  const conditions = ["Original input", "Within-source frame", "Cross-source frame"];
  try {
    const response = await fetch("data/border-audit.json");
    if (!response.ok) throw new Error("Border results unavailable");
    const data = await response.json();
    data.examples.forEach((item, i) => casePicker.add(new Option(item.joint + " example", i)));
    Object.entries(data.results).forEach(([key, result]) => modelPicker.add(new Option(result.name, key)));
    function render() {
      const index = Number(casePicker.value);
      const example = data.examples[index];
      output.replaceChildren(...conditions.map((condition, slot) => {
        const figure = document.createElement("figure");
        const image = new Image(160, 160);
        image.src = example.images[slot];
        image.alt = example.joint + " radiograph, " + condition.toLowerCase();
        const caption = document.createElement("figcaption");
        const values = data.demo[modelPicker.value][index][slot];
        const best = values.indexOf(Math.max(...values));
        const title = document.createElement("strong");
        title.textContent = condition + " · " + data.classes[best];
        const scores = document.createElement("p");
        scores.textContent = values.map((value, i) => data.classes[i] + " " + (value * 100).toFixed(1) + "%").join(" · ");
        caption.append(title, scores);
        figure.append(image, caption);
        return figure;
      }));
    }
    casePicker.addEventListener("change", render);
    modelPicker.addEventListener("change", render);
    render();
  } catch {
    output.textContent = "The saved image comparison could not load. The aggregate results are available below.";
  }
})();

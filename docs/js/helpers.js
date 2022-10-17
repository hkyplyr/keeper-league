async function loadFile(fileName) {
    return await fetch(fileName).then(res => res.json());
}

function replaceContent(elementId, content) {
    var element = document.getElementById(elementId);
    element.innerHTML = "";
    element.append(content);
}
function manage_selection_visibility() {
    all_options = Array.from(document.getElementsByClassName("candidate_select")[0])
                .map(s=>s.getAttribute("class")).slice(1);
    console.log(all_options);
    selects = Array.from(document.getElementsByClassName("candidate_select"));
    selections = selects.map(s=>s.selectedOptions[0].getAttribute("class"));
    console.log(selections);
    all_options.forEach(option=> {
        console.log(selections.indexOf(option))
        if (selections.indexOf(option) > -1) {
            Array.from(document.getElementsByClassName(option))
                .forEach(o => o.setAttribute("hidden", true))
        } else {
            Array.from(document.getElementsByClassName(option))
                .forEach(o => o.removeAttribute("hidden", true))
        }
    })
}
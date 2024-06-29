function show_vote_details(div_id, class_name) {
    target_div = document.getElementById(div_id);
    if (target_div.className == class_name) {
        target_div.setAttribute("class", "")
    } else {
        target_div.setAttribute("class", class_name)
    }
}
async function initialLoad() {
    var week = get_week(5);
    loadPage(week);
}

function get_week(defaultWeek) {
    const urlParams = new URLSearchParams(window.location.search);
    var week = parseInt(urlParams.get('week') || defaultWeek)

    if (week > defaultWeek) {
        return defaultWeek;
    } else {
        return week;
    }
}

async function loadPage(week) {
    updateTitles(week);
    updateStandings(week);
    updatePowerRankings(week);
    updateAwards(week);
    updateTeams(week);
}

async function updateTitles(week) {
    replaceContent("standings-title", `Standings`);
    replaceContent("power-rankings-title", `Power Rankings`);
    replaceContent("awards-title", `Weekly Awards`);
}

async function updateTeams(week) {
    getAllStarTeam(week).then(data => {
        var allStarTeam = document.getElementById("all-star-team");
        allStarTeam.innerHTML = "";

        var header = document.createElement("div");
        header.classList.add("text-2xl", "font-medium", "text-center");
        header.append("⭐️ All-Star Team ⭐️");
        allStarTeam.append(header);

        data.forEach((player, i) => {
            var color = i % 2 ? "bg-white" : "bg-gray-100"

            var playerDiv = document.createElement("div");
            playerDiv.classList.add("flex", "flex-row", "justify-between", "px-3", color);

            var postitionDiv = document.createElement("div");
            postitionDiv.classList.add("text-2xl", "my-auto", "text-center", "font-medium", "w-1/12");
            postitionDiv.append(player.position);

            var imageDiv = document.createElement("div");
            imageDiv.classList.add("px-1");

            var teamImg = document.createElement("img");
            teamImg.classList.add("rounded-full", "team-bg", "w-20", "h-20", "border", "border-black");
            teamImg.src = player.team_image;

            var playerImg = document.createElement("img");
            playerImg.classList.add("rounded-full", "player-img", "w-20", "h-20");
            playerImg.src = player.player_image;

            imageDiv.append(teamImg, playerImg);

            var pointsDiv = document.createElement("div");
            pointsDiv.classList.add("my-auto", "w-1/5", "text-center");
            pointSpan = document.createElement("span");
            pointSpan.classList.add("font-bold", "text-lg");
            pointSpan.append(player.points);
            br = document.createElement("br");
            pointsDiv.append(pointSpan);
            pointsDiv.append(br);
            pointsDiv.append(`${player.avg_points}/gp`);

            var teamDiv = document.createElement("div");
            teamDiv.classList.add("my-auto", "w-1/2", "text-center");
            var playerSpan = document.createElement("span");
            playerSpan.classList.add("font-bold", "text-lg");
            playerSpan.append(player.player);
            teamDiv.append(playerSpan);
            br = document.createElement("br");
            teamDiv.append(br);
            teamDiv.append(player.team);

            playerDiv.append(postitionDiv, imageDiv, teamDiv, pointsDiv);
            allStarTeam.append(playerDiv);
        });
    });

    getAllBustTeam(week).then(data => {
        var allBustTeam = document.getElementById("all-bust-team");
        allBustTeam.innerHTML = "";

        var header = document.createElement("div");
        header.classList.add("text-2xl", "font-medium", "text-center");
        header.append("🗑 All-Bust Team 🗑");
        allBustTeam.append(header);

        data.forEach((player, i) => {
            var color = i % 2 ? "bg-white" : "bg-gray-100"

            var playerDiv = document.createElement("div");
            playerDiv.classList.add("flex", "flex-row", "justify-between", "px-3", color);

            var postitionDiv = document.createElement("div");
            postitionDiv.classList.add("text-2xl", "my-auto", "text-center", "font-medium", "w-1/12");
            postitionDiv.append(player.position);

            var imageDiv = document.createElement("div");
            imageDiv.classList.add("px-1");

            var teamImg = document.createElement("img");
            teamImg.classList.add("rounded-full", "team-bg", "w-20", "h-20", "border", "border-black");
            teamImg.src = player.team_image;

            var playerImg = document.createElement("img");
            playerImg.classList.add("rounded-full", "player-img", "w-20", "h-20");
            playerImg.src = player.player_image;

            imageDiv.append(teamImg, playerImg);

            var pointsDiv = document.createElement("div");
            pointsDiv.classList.add("my-auto", "w-1/5", "text-center");
            pointSpan = document.createElement("span");
            pointSpan.classList.add("font-bold", "text-lg");
            pointSpan.append(player.points);
            br = document.createElement("br");
            pointsDiv.append(pointSpan);
            pointsDiv.append(br);
            pointsDiv.append(`${player.avg_points}/gp`);

            var teamDiv = document.createElement("div");
            teamDiv.classList.add("my-auto", "w-1/2", "text-center");
            var playerSpan = document.createElement("span");
            playerSpan.classList.add("font-bold", "text-lg");
            playerSpan.append(player.player);
            teamDiv.append(playerSpan);
            br = document.createElement("br");
            teamDiv.append(br);
            teamDiv.append(player.team);

            playerDiv.append(postitionDiv, imageDiv, teamDiv, pointsDiv);
            allBustTeam.append(playerDiv);
        });
    });
}

async function updateAwards(week) {
    getAwards(week).then(data => {
        var container = document.createElement("div");
        container.classList.add("flex", "flex-wrap", "gap-y-3", "text-center");

        data.forEach(row => {
            var div = document.createElement("div");
            div.classList.add("flex", "flex-col", "justify-center", "w-1/4");

            var imageDiv = document.createElement("div");
            imageDiv.classList.add("mx-auto");

            var image = document.createElement("img");
            image.src = row.image;
            image.classList.add("rounded-full", "border", "w-40", "h-40", "border-black");

            imageDiv.append(image);

            var label = document.createElement("div");
            label.classList.add("font-bold");
            label.append(row.label);

            var value = document.createElement("div");
            value.append(row.value);

            div.append(imageDiv, label, value);
            container.append(div);
        });

        replaceContent("awards-table", container);
    });
}

async function updatePowerRankings(week) {


    getPowerRankings(week).then(data => {
        var powerRankings = document.getElementById("power-rankings-table");
        powerRankings.innerHTML = "";

        data.forEach(row => {
            var container = document.createElement("div");
            container.classList.add("flex-col", "w-full", row.color, "rounded-md");

            var topContainer = document.createElement("div");
            topContainer.classList.add("ranking-header", "flex", "flex-row", "w-full", "rounded-t-md", "text-3xl", "font-bold", "border", "border-black", "border-b-0", "p-1");

            var nameContainer = document.createElement("div");
            nameContainer.classList.add("flex-col", "w-1/2")
            nameContainer.append(`${row.rank}. ${row.team}`);
    
            var resultContainer = document.createElement("div");
            resultContainer.classList.add("flex-col", "w-1/2", "text-center")
            resultContainer.append(`${row.result} - ${row.points}`);
    
            var movementContainer = document.createElement("div");
            movementContainer.classList.add("flex-col", "w-1/6", "text-center")

            var movement = "-"
            if (row.movement < 0) {
                movement = "▼"
            } else if (row.movement > 0) {
                movement = "▲"
            } else {
                movement = "—"
            }

            movementContainer.append(movement);

            var bottomContainer = document.createElement("div");
            bottomContainer.classList.add("bg-white", "rounded-b-md", "border", "border-black", "border-t-0", "p-1")
    
            var middle = document.createElement("div");
            middle.classList.add("flex", "flex-row", "w-full", "italic", "pb-2");
    
            var topPlayerContainer = document.createElement("div");
            topPlayerContainer.classList.add("text-left", "w-1/4", "whitespace-nowrap")
            topPlayerContainer.append(`Top Player: ${row.top_player}`);
    
            var weeklyCoachContainer = document.createElement("div");
            weeklyCoachContainer.classList.add("text-center", "w-1/4")
            weeklyCoachContainer.append(`Weekly Coach Rating: ${row.weekly_coach_percentage}%`);
    
            var totalPointsContainer = document.createElement("div");
            totalPointsContainer.classList.add("text-center", "w-1/4")
            totalPointsContainer.append(`Total PF: ${row.total_points}`);
    
            var yearlyCoachContainer = document.createElement("div");
            yearlyCoachContainer.classList.add("text-right", "w-1/4")
            yearlyCoachContainer.append(`Yearly Coach Rating: ${row.yearly_coach_percentage}%`);

            var writeup = document.createElement("div");
            writeup.append(row.writeup);

            middle.append(topPlayerContainer, weeklyCoachContainer, totalPointsContainer, yearlyCoachContainer);
    
            topContainer.append(nameContainer, resultContainer, movementContainer);
            bottomContainer.append(middle, writeup);
            container.append(topContainer, bottomContainer);
            powerRankings.append(container);
        });
    });
}

async function updateStandings(week) {
    getStandings(week)
        .then(data => {
            var thead = document.createElement("thead");
            var header_row = document.createElement("tr");
            ["", "Record", "All Play", "PF", "OPF", "Coach %", "Luck %"].forEach(header => {
                var cell = document.createElement("th");
                cell.append(header);
                header_row.append(cell)
            });
            thead.append(header_row);

            var tbody = document.createElement("tbody");
            data.forEach(row =>
                addStandingRow(row, tbody));

            var table = document.getElementById("standings-table");
            table.innerHTML = "";
            table.append(thead, tbody);
        })
}

function buildCell(content, classList = "") {
    var cell = document.createElement("td");

    if (classList) {
        cell.classList.add(classList);
    }

    cell.append(content);
    return cell;
}

async function addStandingRow(row, tbody) {
    var teamName = `${row.rank}. ${row.team}`

    var team = buildCell(teamName, "text-left");
    var record = buildCell(row.record);
    var all_play = buildCell(row.all_play);
    var pf = buildCell(row.points_for);
    var opf = buildCell(row.optimal_points_for);
    var coach = buildCell(row.coach_percentage);
    var luck = buildCell(row.luck_percentage);

    var row = document.createElement("tr");
    row.classList.add("border");
    row.append(team, record, all_play, pf, opf, coach, luck);

    tbody.append(row)
}

async function getStandings(week) {
    return await loadFile(`./data/week-${week}.json`)
        .then(json => json.standings);
}

async function getPowerRankings(week) {
    return await loadFile(`./data/week-${week}.json`)
        .then(json => json.powerRankings);
}

async function getAwards(week) {
    return await loadFile(`./data/week-${week}.json`)
        .then(json => json.awards);
}

async function getAllStarTeam(week) {
    return await loadFile(`./data/week-${week}.json`)
        .then(json => json.allStarTeam);
}

async function getAllBustTeam(week) {
    return await loadFile(`./data/week-${week}.json`)
        .then(json => json.allBustTeam);
}
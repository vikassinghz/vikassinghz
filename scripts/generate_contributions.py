import json
import os
import urllib.request


USERNAME = "vikassinghz"
OUTPUT = "profile/contributions.svg"


QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        colors
        weeks {
          firstDay
          contributionDays {
            date
            contributionCount
            color
            weekday
          }
        }
        months {
          name
          firstDay
          totalWeeks
        }
      }
    }
  }
}
"""


def get_calendar():
    token = os.environ["GITHUB_TOKEN"]

    payload = json.dumps({
        "query": QUERY,
        "variables": {
            "login": USERNAME
        }
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-profile-stats"
        }
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode())

    if "errors" in result:
        raise RuntimeError(result["errors"])

    return result["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def generate_svg(calendar):

    weeks = calendar["weeks"]
    total = calendar["totalContributions"]
    colors = calendar["colors"]

    cell_size = 12
    gap = 3
    step = cell_size + gap

    left = 45
    top = 55

    width = left + len(weeks) * step + 20
    height = top + (7 * step) + 45

    svg = []

    svg.append(
        f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{width}"
        height="{height}"
        viewBox="0 0 {width} {height}">'''
    )

    # Background
    svg.append(
        f'''
        <rect width="100%" height="100%"
        rx="12"
        fill="#0D1117"/>'''
    )

    # Title
    svg.append(
        f'''
        <text
        x="20"
        y="30"
        fill="#E6EDF3"
        font-family="Arial, sans-serif"
        font-size="17"
        font-weight="600">
        GitHub Contributions — {total} in the last year
        </text>'''
    )

    # Month labels
    for month in calendar["months"]:

        week_index = None

        for index, week in enumerate(weeks):
            if week["firstDay"] == month["firstDay"]:
                week_index = index
                break

        if week_index is not None:

            x = left + week_index * step

            svg.append(
                f'''
                <text
                x="{x}"
                y="48"
                fill="#8B949E"
                font-family="Arial, sans-serif"
                font-size="11">
                {month["name"][:3]}
                </text>'''
            )

    # Weekday labels
    weekday_labels = {
        1: "Mon",
        3: "Wed",
        5: "Fri"
    }

    for weekday, label in weekday_labels.items():

        y = top + (weekday - 1) * step + 10

        svg.append(
            f'''
            <text
            x="5"
            y="{y}"
            fill="#8B949E"
            font-family="Arial, sans-serif"
            font-size="10">
            {label}
            </text>'''
        )

    # Contribution squares
    for week_index, week in enumerate(weeks):

        x = left + week_index * step

        for day in week["contributionDays"]:

            row = day["weekday"] - 1
            y = top + row * step

            count = day["contributionCount"]
            color = day["color"]
            date = day["date"]

            svg.append(
                f'''
                <rect
                x="{x}"
                y="{y}"
                width="{cell_size}"
                height="{cell_size}"
                rx="3"
                fill="{color}">
                    <title>{count} contributions on {date}</title>
                </rect>'''
            )

    # Legend
    legend_y = height - 15

    svg.append(
        f'''
        <text
        x="{left}"
        y="{legend_y}"
        fill="#8B949E"
        font-family="Arial, sans-serif"
        font-size="10">
        Less
        </text>'''
    )

    for index, color in enumerate(colors):

        x = left + 30 + index * 18

        svg.append(
            f'''
            <rect
            x="{x}"
            y="{legend_y - 10}"
            width="12"
            height="12"
            rx="3"
            fill="{color}"/>'''
        )

    svg.append(
        f'''
        <text
        x="{left + 30 + len(colors) * 18 + 5}"
        y="{legend_y}"
        fill="#8B949E"
        font-family="Arial, sans-serif"
        font-size="10">
        More
        </text>'''
    )

    svg.append("</svg>")

    return "\n".join(svg)


def main():

    os.makedirs("profile", exist_ok=True)

    calendar = get_calendar()

    svg = generate_svg(calendar)

    with open(OUTPUT, "w", encoding="utf-8") as file:
        file.write(svg)

    print(
        f"Generated {OUTPUT} "
        f"with {calendar['totalContributions']} contributions."
    )


if __name__ == "__main__":
    main()

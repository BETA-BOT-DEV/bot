def rank(rank):
    match rank:
        case "x":
            return "<:x_:1041078925842985022>"
        case "u":
            return "<:u_:1041078925188681789>"
        case "ss":
            return "<:ss:1041078923636781148>"
        case "s+":
            return "<:sp:1041078922898571366>"
        case "s":
            return "<:s_:1041078921820635227>"
        case "s-":
            return "<:sm:1041078920591720478>"
        case "a+":
            return "<:ap:1041078919438278737>"
        case "a":
            return "<:a_:1041078918221934723>"
        case "a-":
            return "<:am:1041078916611309590>"
        case "b+":
            return "<:bp:1041078915722129478>"
        case "b":
            return "<:b_:1041078914384146483>"
        case "b-":
            return "<:bm:1041078913650139257>"
        case "c+":
            return "<:cp:1041078912568004790>"
        case "c":
            return "<:c_:1041078911188078714>"
        case "c-":
            return "<:cm:1041078909741056040>"
        case "d+":
            return "<:dp:1041078908671512677>"
        case "d":
            return "<:d_:1041078907664859186>"
        case "z":
            return "<:z:1041078927264858162>"


def badges(json):
    badges = ""
    badgeEmojis = [json[i]["id"] for i in range(len(json))]
    for badgeEmoji in badgeEmojis:
        match badgeEmoji:
            case "100player":
                badges += "<:zSL:847188404163837953>"
            case "20tsd":
                badges += "<:z20tsd:847188471633674270>"
            case "allclear":
                badges += "<:zPC:847188524247285771>"
            case "early-supporter":
                badges += "<:zES:847188570769850380>"
            case "infdev":
                badges += "<:zINF:847189521899454505>"
            case "kod_founder":
                badges += "<:zKOD:847188743680557146>"
            case "leaderboard1":
                badges += "<:zRank1:847188809907961886>"
            case "secretgrade":
                badges += "<:zSG:847188855865868338>"
            case "superlobby":
                badges += "<:zHDSL:847190320986325034>"
    return badges

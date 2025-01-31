from fastapi import APIRouter, Body, HTTPException
from typing import List

from db import get_entries as get_entries_db
from utils.types import Player, AllFilters


router = APIRouter()


@router.get("/player/{profile}")
async def player(profile: str) -> Player:
    """
    Returns a list of entries from the database given a filter.
    """
    # Using by_alias to convert the filters to the database format.
    data = await get_entries_db({"profile": profile})
    if not data:
        raise HTTPException(status_code=404, detail=f"No player with profile '{profile}'")
    fields = ["wins", "winsSwiss", "winsBracket", "draws", "losses", "lossesSwiss", "lossesBracket"]
    out: Player = {field: 0 for field in fields}
    out['tournaments'] = []
    out['name'] = data[0].get('name', "")
    out['profile'] = profile

    topCuts = 0
    
    for entry in data:
        for field in fields:
            out[field] += entry.get(field, 0)
        if entry.get('standing', float('inf')) <= entry.get('topCut', 0):
            topCuts += 1
        out['tournaments'].append(entry)
    
    out["winRate"] = out["wins"] / (out["wins"] + out["draws"] + out["losses"])
    out["winRateSwiss"] = out["winsSwiss"] / (out["winsSwiss"] + out["draws"] + out["lossesSwiss"])
    out["winRateBracket"] = out["winsBracket"] / (out["winsBracket"] + out["lossesBracket"])
    out["conversionRate"] = topCuts / len(out["tournaments"])
    out["topCuts"] = topCuts

    return out
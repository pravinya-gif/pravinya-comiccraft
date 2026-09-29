def build_comic_layout(outline: list[dict], story: list[dict], image_paths: list[str]) -> list[dict]:
    story_by_num = {int(p.get("panel_number", i+1)): p for i, p in enumerate(story)}
    layout = []
    for i, panel in enumerate(outline):
        number = int(panel.get("panel_number", i+1))
        narrative = story_by_num.get(number, {})
        layout.append({
            **panel,
            "image_path": image_paths[i] if i < len(image_paths) else "",
            "narration": narrative.get("narration", ""),
            "dialogue": narrative.get("dialogue", ""),
        })
    return layout

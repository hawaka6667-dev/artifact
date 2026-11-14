# artifact

Source for pages published as Claude artifacts. GitHub holds the source; each artifact is the published copy.

## Layout

One folder per artifact, named `<slug>-v<version>`. Each folder holds the page and a small `artifact.json` with the artifact URL and version.

| Folder | Artifact | Version |
| --- | --- | --- |
| `sky-clocks-v4/` | 三重天文钟: eccentric, lunar and 24-hour sky clocks | 4 |
| `maze-lab-v1794460546-92df/` | Maze Lab: 10 generators, 9 solvers, structure metrics | version id `1794460546-92df` |

`sky-clocks-v4/tests/` holds node scripts that check the astronomy and the render path:

```
node sky-clocks-v4/tests/check.js          # equinox, solstice, eclipse, ascendant, eccentric model
node sky-clocks-v4/tests/seasons_check.js  # solar terms and season lengths
node sky-clocks-v4/tests/sat_check.js      # Saturn oppositions
node sky-clocks-v4/tests/smoke.js          # render path in zh and en with a stub DOM
```

## Workflow

1. Edit `index.html` in the artifact's folder.
2. Run its checks, if it has any.
3. Commit.
4. Republish the same file to the `url` in `artifact.json`, using the commit message as the publish label.
5. Rename the folder to the new version and update `artifact.json`.

Pushing to GitHub does not update the artifact. Publishing happens only when a Claude session calls the Artifact tool.

## Pages

`index.html` is the authoring format: no doctype, `<head>` or `<body>`, because the Artifact tool wraps the page when it publishes. A GitHub Pages build would need to add the same wrapper (doctype, charset and viewport meta) first.

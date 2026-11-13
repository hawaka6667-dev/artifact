# artifact

Source for pages published as Claude artifacts. GitHub holds the source; the artifact is the published copy.

## Layout

```
sky-clocks/
  index.html   the whole page (HTML, CSS, JS in one file)
  tests/       node scripts that check the astronomy and the render path
```

## sky-clocks

Three astronomical clocks with a zh / EN toggle: an eccentric clock with a four-seasons layer, a lunar orbit clock, and a 24-hour sky clock with Sun, Moon, rising sign and Saturn. Time, latitude, longitude and city are adjustable.

Published at https://claude.ai/artifact/3fT18199Xg9VFhyYBgffpX (private to the owner).

Run the checks from the repo root:

```
node sky-clocks/tests/check.js          # equinox, solstice, eclipse, ascendant, eccentric model
node sky-clocks/tests/seasons_check.js  # solar terms and season lengths
node sky-clocks/tests/sat_check.js      # Saturn oppositions
node sky-clocks/tests/smoke.js          # render path in zh and en with a stub DOM
```

## Workflow

1. Edit `sky-clocks/index.html`.
2. Run the checks.
3. Commit.
4. Republish the same file to the artifact URL, using the commit message as the publish label.

Pushing to GitHub does not update the artifact. Publishing happens only when a Claude session calls the Artifact tool.

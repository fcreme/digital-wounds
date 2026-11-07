# Artist Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every painting in the gallery becomes a sharp piece owned by a tattoo artist, and pressing E on one opens a full-screen, page-turning view of that artist's designs.

**Architecture:** Artists are data folders under `assets/artists/`. Paintings are a data file listing each one's wall position, artist and design, generated from rectangles marked on the model's texture. The game draws each painting as one quad just in front of the wall, and picks the painting under the crosshair with a ray test. Logic with no OpenGL lives in small files with CTest unit tests, and everything visual is checked through a scripted test driver that saves frames.

**Tech Stack:** C++17, SDL2, OpenGL 3.3 (GLSL 330), nlohmann/json, stb_image, CMake/CTest. Tools are Python 3 standard library only, since numpy and PIL aren't installed.

**Spec:** `docs/superpowers/specs/2026-11-06-artist-discovery-design.md`

## Global Constraints

- No new dependencies in the game. Python tools use the standard library only.
- Coding conventions from `CLAUDE.md`: class names `PascalCase`, methods `camelCase`, members `m_`, `#pragma once`.
- Commit messages are plain, with no `Co-Authored-By` or session trailers. Work stays on branch `mac-support`.
- Prompt text is exactly `Press E to see the artist`. Hint text is exactly `A/D: Turn page   Q: Close`.
- Adding an artist or reassigning a painting must never need a C++ change.
- All text uses `UIOverlay::drawText`, which covers ASCII 32 to 122 with `&` blank.
- Stand-in names must be obviously fictional, and no real person's name or work is used. Dark Ink Studio keeps its name and text.
- Don't change the model file, `hallway.json`, `studio.json`, `test_room.json` or anything under `legacy/`.

## Review Focus

- **A broken artist folder** (missing image, bad JSON, painting naming an unknown artist or design) should log one clear error and leave the game running, not crash or drop the whole catalog. Tests in Tasks 3 and 4.
- **Looking at the gap between two frames, or at a frame seen from behind or very far away,** should offer no prompt, not the nearest painting. Tests in Task 4.
- **Pressing keys at the edges of the artist view** (A on the first page, D on the last, E or Q during the open animation) should do nothing odd. Test in Task 8.
- **Resizing the window or moving it between Retina and non-Retina displays** should keep the image sharp and the text inside its column, including while the artist view is open. Checks in Tasks 2 and 8, plus a minimum window size.
- **Long or non-ASCII text in an artist file** should warn at load and still display without overflow. Tests in Tasks 3 and 8.

---

## File Structure

| Path | Responsibility |
|---|---|
| `src/core/TestDriver.{h,cpp}` | Scripted input, frame saving and state logging. Compiled only with `-DDW_TEST_DRIVER=ON` |
| `src/world/ArtistCatalog.{h,cpp}` | Loads and validates artists. No OpenGL |
| `src/world/PaintingData.{h,cpp}` | Loads the painting list, resolves it against the catalog, and picks by ray. No OpenGL |
| `src/world/PaintingWall.{h,cpp}` | Owns wall textures and draws the paintings |
| `src/ui/TextLayout.{h,cpp}` | Text wrapping and artist view layout. No OpenGL |
| `src/ui/ArtistView.{h,cpp}` | Full-screen artist view |
| `assets/shaders/painting.{vert,frag}` | Unlit frame, mat and artwork on one quad |
| `assets/artists/<id>/` | `artist.json` and images |
| `assets/paintings/museum.json` | Generated painting list |
| `tools/glb_walls.py` | Reads wall triangles and texture coordinates from the GLB |
| `tools/data/painting_rects.json` | Painting rectangles marked by hand on the texture |
| `tools/build_paintings.py` | Rectangles to world positions, assignment, and the checking overlay |
| `tools/gen_standins.py` | Generates stand-in artists and drawings |
| `tests/` | `dw_tests` unit tests, Python tool tests, driver scripts |

---

### Task 1: Test infrastructure and asset copying

Everything later relies on this. It also fixes a trap: assets are copied only when the executable relinks, so data-only edits never reach `build/`.

**Files:**
- Create: `src/core/TestDriver.h`, `src/core/TestDriver.cpp`, `tests/test_main.cpp`, `tests/test_util.h`, `tests/scripts/smoke.txt`
- Modify: `CMakeLists.txt`, `src/core/Engine.cpp`, `src/scene/Scene.cpp`, `.gitignore`

**Interfaces:**
- Produces: the build option `DW_TEST_DRIVER`; running `./digital_wounds --script <path>`; the macro `TEST(name)` and `CHECK(cond)` in `tests/test_util.h`; the target `dw_tests`.
- Script commands, one per line, with `#` comments:
  - `wait <seconds>`
  - `key <down|up|tap> <SDL scancode name>`
  - `mouse <dx> <dy>`
  - `shot <name>` saves `shots/<name>.bmp` at drawable size
  - `pos <label>` logs camera x and z
  - `state <label>` logs `DRIVER state <label> near=<painting id or none> view=<open|closed> artist=<id> page=<n>`
  - `sizes` logs `DRIVER sizes window=WxH drawable=WxH`
  - `fps` logs average fps
  - `quit`

- [ ] **Step 1: Write `tests/scripts/smoke.txt`**

Script: `wait 1`, `sizes`, `shot smoke`, `fps`, `quit`.

- [ ] **Step 2: Run it to verify it fails**

Run: `cmake -B build-test -DCMAKE_BUILD_TYPE=Release -DDW_TEST_DRIVER=ON && cmake --build build-test -j8 && cd build-test && ./digital_wounds --script ../tests/scripts/smoke.txt`
Expected: the option has no effect, the game ignores the argument, and no `shots/smoke.bmp` appears.

- [ ] **Step 3: Implement the driver and build changes**

- `TestDriver` has `bool load(path)`, `void beforeUpdate(InputManager&)` called right after `processEvents`, and `void afterRender(Engine&)` called right before `SDL_GL_SwapWindow`. Mouse and key `tap` events must be injected in `beforeUpdate`, because `preUpdate` clears them.
- With the driver active, `Engine::processEvents` drops every real event except `SDL_QUIT`, and `Scene` doesn't grab the mouse. Real input reaching the window has already spoiled earlier runs.
- Guard all driver code with `#ifdef DW_TEST_DRIVER`, so the normal build has none of it.
- Replace the two `POST_BUILD` copy commands with an `add_custom_target(copy_assets ALL ...)` the game depends on, so asset copies happen on every build.
- Add `dw_tests` and `enable_testing()`. It compiles only the OpenGL-free files it lists, and starts with one trivial test so the target exists.
- Add `build-test/` to `.gitignore`.

- [ ] **Step 4: Run it to verify it passes**

Run the Step 2 command, then `ctest --test-dir build-test --output-on-failure`.
Expected: logs `DRIVER sizes` and an fps line, `build-test/shots/smoke.bmp` exists and shows the gallery, and CTest reports 1 test passing with no failures.

- [ ] **Step 5: Confirm the normal build is unaffected**

Run: `cmake --build build -j8 && command grep -a -c DRIVER build/digital_wounds`
Expected: builds, and the count is `0`.

- [ ] **Step 6: Commit**

```bash
git add CMakeLists.txt .gitignore src/core/TestDriver.h src/core/TestDriver.cpp src/core/Engine.cpp src/scene/Scene.cpp tests
git commit -m "Add scripted test driver, unit test target and reliable asset copying"
```

---

### Task 2: Retina sharpness

**Files:**
- Modify: `src/core/Engine.h`, `src/core/Engine.cpp`, `src/renderer/Renderer.cpp`, `src/fx/PostProcess.cpp`
- Create: `tests/scripts/retina.txt`

**Interfaces:**
- Produces: `Engine` members `m_drawableWidth`, `m_drawableHeight` in pixels. `m_windowWidth` and `m_windowHeight` keep meaning logical UI units. Later tasks take UI sizes in logical units.

- [ ] **Step 1: Write `tests/scripts/retina.txt`**

Script: `wait 2`, `sizes`, `shot retina_before`, `fps`, `quit`.

- [ ] **Step 2: Run it to verify it fails**

Expected: `drawable=1280x720 window=1280x720`.

- [ ] **Step 3: Implement**

- Add `SDL_WINDOW_ALLOW_HIGHDPI` and call `SDL_GetDrawableSize` after the context is created.
- `Renderer` and `PostProcess` receive drawable size. This covers the shadow pass restore in `Renderer.cpp`, `glViewport` in `Engine.cpp`, and the size passed to `setDepthTexture`.
- `UIOverlay` keeps logical size. It maps to NDC, so it works under the larger viewport unchanged.
- Handle `SDL_WINDOWEVENT_SIZE_CHANGED` instead of `RESIZED`, re-reading both sizes. This also covers moving between displays.
- Call `SDL_SetWindowMinimumSize(window, 960, 540)`.
- `Scene`'s camera aspect must stay correct after a resize. Check this rather than assume it, because it reads `renderer.getWidth()` only at room load.

- [ ] **Step 4: Run it to verify it passes**

Run the script again and open `shots/retina_before.bmp` at full size.
Expected: `drawable` is 2× `window`, edges are visibly sharper than the earlier 1280×720 frames, the crosshair and prompt are their usual size and centred, and fps is at least 50.

- [ ] **Step 5: If fps is below 50, halve the SSAO buffers**

Set `m_ssaoWidth = width / 2` and `m_ssaoHeight = height / 2` in `PostProcess`, in both creation and `onResize`, and re-measure. If it's still below 50, stop and report rather than lowering anything else.

- [ ] **Step 6: Commit**

```bash
git add src/core src/renderer/Renderer.cpp src/fx/PostProcess.cpp tests/scripts/retina.txt
git commit -m "Render at full Retina resolution"
```

---

### Task 3: Artist catalog

**Files:**
- Create: `src/world/ArtistCatalog.h`, `src/world/ArtistCatalog.cpp`, `tests/test_artist_catalog.cpp`, `tests/fixtures/artists/*`

**Interfaces:**
- Produces:

```cpp
struct ArtistDesign { std::string id, title, description, imagePath; };
struct Artist { std::string id, name, description; std::vector<ArtistDesign> designs; };
class ArtistCatalog {
public:
    int loadFromDirectory(const std::string& dir);  // returns artists loaded; logs problems to cerr
    const Artist* find(const std::string& id) const;
    const std::vector<Artist>& artists() const;
    const std::vector<std::string>& warnings() const;
};
constexpr size_t MAX_NAME_CHARS = 28, MAX_ARTIST_DESC_CHARS = 120, MAX_TITLE_CHARS = 40, MAX_DESIGN_DESC_CHARS = 200;
```

- File format, `assets/artists/<id>/artist.json`, with the folder name as the artist id:

```json
{ "name": "Dark Ink Studio", "description": "...",
  "designs": [ { "id": "ravens-eye", "title": "The Raven's Eye", "description": "...", "image": "ravens-eye.png" } ] }
```

- [ ] **Step 1: Write failing tests in `tests/test_artist_catalog.cpp`**

Fixtures: `good`, `bad-json`, `missing-image`, `no-designs`, `too-long`, `accented`.

```cpp
TEST(loadsGoodArtist)        // find("good") has name, 2 designs, imagePath under its folder
TEST(badJsonSkipsOnlyThatArtist)   // find("bad-json")==nullptr, find("good")!=nullptr
TEST(artistWithNoDesignsIsSkipped)
TEST(missingImageDropsThatDesignAndWarns)  // 1 design remains, warnings() mentions the file
TEST(tooLongTextIsTruncatedAndWarns)       // name.size()==MAX_NAME_CHARS
TEST(unsupportedCharactersWarn)            // "José" and "Ink & Blood" each warn, text kept
TEST(missingDirectoryReturnsZero)
```

- [ ] **Step 2: Run to verify they fail**

Run: `cmake --build build-test -j8 --target dw_tests && ctest --test-dir build-test --output-on-failure`
Expected: fails to compile, `ArtistCatalog` isn't defined.

- [ ] **Step 3: Implement `ArtistCatalog`**

Sort artists by id so the order doesn't depend on the filesystem. Unsupported means a byte outside ASCII 32 to 122, or `&`. Truncation counts bytes.

- [ ] **Step 4: Run to verify they pass**

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/world/ArtistCatalog.h src/world/ArtistCatalog.cpp tests CMakeLists.txt
git commit -m "Add artist catalog loaded from data folders"
```

---

### Task 4: Painting data and picking

**Files:**
- Create: `src/world/PaintingData.h`, `src/world/PaintingData.cpp`, `tests/test_painting_data.cpp`

**Interfaces:**
- Consumes: `ArtistCatalog` from Task 3.
- Produces:

```cpp
struct Painting {
    std::string id, artistId, designId;
    glm::vec3 center, right, up, normal;  // unit vectors; normal faces into the room
    glm::vec2 size;                       // full width and height in world units
    int designIndex = -1;                 // index in the artist's designs
};
std::vector<Painting> loadPaintings(const std::string& path, const ArtistCatalog& catalog);
int pickPainting(const std::vector<Painting>& paintings, const glm::vec3& eye, const glm::vec3& lookDir, float maxDistance = 16.0f);
```

- File format, `assets/paintings/museum.json`: `{ "paintings": [ { "id": "...", "center": [x,y,z], "right": [x,y,z], "normal": [x,y,z], "size": [w,h], "artist": "...", "design": "..." } ] }`. `up` is computed as `normal × right`.

- [ ] **Step 1: Write failing tests**

```cpp
TEST(picksPaintingUnderCrosshair)     // eye faces centre of painting A: returns A
TEST(picksAmongNeighbours)            // A and B 0.1 apart: aiming at B returns B, not the first in the list
TEST(gapBetweenFramesPicksNothing)    // aim at the gap: returns -1
TEST(behindPaintingPicksNothing)      // eye on the wall side: -1
TEST(tooFarPicksNothing)              // farther than maxDistance: -1
TEST(nearestWinsWhenOverlapping)      // two along the ray: the nearer
TEST(emptyListPicksNothing)
TEST(topRowPickableFromFloor)         // eye y=5, painting at y=10 on a wall 2 units away, looking up: picks it
TEST(unknownArtistOrDesignIsSkipped)  // loadPaintings keeps the valid entries, logs the rest
TEST(missingFileReturnsEmpty)
```

- [ ] **Step 2: Run to verify they fail**

Expected: fails to compile.

- [ ] **Step 3: Implement**

`pickPainting` intersects the ray with each painting's plane, rejecting a hit when the ray isn't heading toward the front face (`dot(lookDir, normal) >= 0`), then tests the hit point against the rectangle. Return the nearest. This replaces the book system's 30° cone, which can't tell packed frames apart.

- [ ] **Step 4: Run to verify they pass**

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/world/PaintingData.h src/world/PaintingData.cpp tests CMakeLists.txt
git commit -m "Add painting data and crosshair picking"
```

---

### Task 5: Find every painting's position

This is the largest manual effort. Do it wall by wall.

**Files:**
- Create: `tools/glb_walls.py`, `tools/build_paintings.py`, `tools/data/painting_rects.json`, `tests/test_build_paintings.py`

**Interfaces:**
- Produces: `tools/data/painting_rects.json`, as `{ "rects": [ { "id": "r001", "uv": [u0, v0, u1, v1] } ] }`, where `uv` is in the emissive texture's 0 to 1 space with v from the top, and it encloses the whole frame. Also `rect_to_world(rect, triangles) -> dict` returning `center, right, normal, size`, offset 0.03 units off the wall.
- The model has 48 triangles. Scale all positions by 10. The emissive texture is image 1 and uses `TEXCOORD_1`, in the same top-left space as the rectangles, with no flip.

- [ ] **Step 1: Write failing tests**

```python
def test_rect_on_known_wall_maps_to_expected_world_position():
    # West wall: x=-10, z from -33.24 to -7.49, y 0 to 10.9; uv u 0.58..0.72, v 0.19..0.52
    # A rect at that uv range's centre lands at x=-9.97 (0.03 into the room), mid wall
def test_normal_faces_into_the_room():      # dot(normal, hall_centre - center) > 0
def test_rect_outside_any_wall_raises():    # floor or empty texture area is an error
def test_rect_spanning_two_triangles_of_a_wall_works():
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tests/test_build_paintings.py`
Expected: fails, `build_paintings` doesn't exist.

- [ ] **Step 3: Implement `glb_walls.py` and `rect_to_world`**

Keep only vertical triangles (`|normal.y| < 0.3`). A wall is affine in texture space, so map rectangle corners with barycentric coordinates from the containing triangle. Choose the normal sign to face the hall centre at (1.5, 5, -1.5). Note the notch at z -7.49 to 2.08: its side walls are real walls too.

- [ ] **Step 4: Run to verify they pass**

Expected: all pass.

- [ ] **Step 5: Add the checking overlay**

`python3 tools/build_paintings.py --overlay out.png` writes the atlas with every rectangle outlined and numbered. PNG decode and encode with `zlib` and `struct`.

- [ ] **Step 6: Mark the rectangles**

Work region by region at high zoom, using `sips -c` to crop. The painted regions of the 1024-pixel texture are, as x and y ranges:

| Region | x | y |
|---|---|---|
| Top-left end wall | 0-125 | 35-190 |
| Doorway wall | 600-740 | 190-300 |
| Left long strip | 600-740 | 430-1024 |
| Top centre | 740-880 | 10-320 |
| Top right | 885-1024 | 15-320 |
| Middle right | 740-915 | 320-650 |
| Lower right | 745-885 | 650-1024 |

Enclose whole frames, not just canvases, with no margin past the frame. Leave out rope posts, chairs, the doorway and its stairs, and the window panels.

- [ ] **Step 7: Verify the rectangles**

Run the overlay and read it region by region.
Expected: every framed painting has exactly one outline fully enclosing it, none is missed, and the total is recorded in the commit message.

- [ ] **Step 8: Commit**

```bash
git add tools tests/test_build_paintings.py
git commit -m "Record every gallery painting's position from the model texture"
```

---

### Task 6: Stand-in artists and painting assignment

**Files:**
- Create: `tools/gen_standins.py`, `assets/artists/*`, `assets/paintings/museum.json`
- Modify: `tools/build_paintings.py`, `tests/test_build_paintings.py`, `assets/rooms/museum.json`

**Interfaces:**
- Consumes: the `artist.json` format from Task 3, the painting format from Task 4, the rectangles from Task 5.
- Produces: `assets/paintings/museum.json`, and the room field `"paintings": "assets/paintings/museum.json"` that Task 7 reads.

- [ ] **Step 1: Write failing tests**

```python
def test_every_rect_gets_exactly_one_design():      # no design used twice, none left unused
def test_same_artist_not_side_by_side():            # neighbours within 4 world units on a wall differ
def test_assignment_is_deterministic():             # two runs produce identical output
def test_each_artist_appears_on_at_least_two_walls():
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tests/test_build_paintings.py`
Expected: fails on the new tests.

- [ ] **Step 3: Implement `build_paintings.py --assign`**

Use a fixed seed, greedily choosing the artist with the most designs left who isn't used nearby.

- [ ] **Step 4: Implement `tools/gen_standins.py`**

- 20 artists, `dark-ink` included, using its existing name, description and first four designs from `public/data/artists/dark-ink/config.json`.
- Design counts add up to the number of rectangles, as evenly as possible.
- Each invented artist gets an obviously fictional name, a distinct tattoo style and a drawing vocabulary, so the styles differ visibly on the wall.
- Images are 1024 pixels on the long side, black ink on the paper colour `#E6DCC8`, rasterized with a small polygon and line routine, and written as PNG. They should read as tattoo flash, not blank boxes.
- All text passes `ArtistCatalog`'s limits and character set.
- A fixed seed makes output identical between runs.

- [ ] **Step 5: Generate and check**

Run: `python3 tools/gen_standins.py && python3 tools/build_paintings.py --assign && python3 -m unittest tests/test_build_paintings.py`
Expected: tests pass, and a small `dw_tests` case added here loads the real `assets/artists` and `assets/paintings/museum.json` with zero warnings, zero skipped entries, and the same painting count as the rectangles. Read several generated images to confirm each looks like a tattoo design.

- [ ] **Step 6: Commit**

```bash
git add tools tests assets/artists assets/paintings assets/rooms/museum.json
git commit -m "Add stand-in artists and assign every painting"
```

---

### Task 7: Hang the paintings

**Files:**
- Create: `src/world/PaintingWall.h`, `src/world/PaintingWall.cpp`, `assets/shaders/painting.vert`, `assets/shaders/painting.frag`, `tests/scripts/walls.txt`
- Modify: `src/renderer/Texture.h`, `src/renderer/Texture.cpp`, `src/scene/Room.h`, `src/scene/Room.cpp`, `src/scene/Scene.h`, `src/scene/Scene.cpp`

**Interfaces:**
- Consumes: `ArtistCatalog`, `loadPaintings`, `Painting`, and the room field `paintings`.
- Produces: `Texture::loadScaled(path, bool sRGB, int maxSize)`; `PaintingWall::load(paintings, catalog)`, `render(camera, highlightedIndex, highlightAmount)`, `shutdown()`; the room field `painting_brightness`, a float defaulting to 1.0; and `Scene` members `m_catalog`, `m_paintings`, `m_paintingWall`.

- [ ] **Step 1: Write `tests/scripts/walls.txt`**

From the centre: look in 8 directions, shooting each. Then walk to each end of the hall and shoot both side walls.

- [ ] **Step 2: Run to verify it fails**

Expected: frames still show the old-master paintings.

- [ ] **Step 3: Implement `Texture::loadScaled`**

Halve with a box filter until the long side is at most `maxSize`, then upload with mipmaps. Don't flip. Wall images use `maxSize` 512, so roughly 120 images stay around 170 MB of texture memory.

- [ ] **Step 4: Implement the shader and `PaintingWall`**

- One quad per painting. Images are read with top-left UVs.
- From the outside in: a dark frame 6% of the short side, the paper mat colour, and the artwork centred and fitted without stretching.
- Unlit. Output is `texture * uBrightness`, with the image flagged sRGB, the same way the room is treated. Add a warm frame glow from `uHighlight`, on the frame only.
- `museum.json` sets `painting_brightness` to 2.0. Tune it only if the on-screen paper colour clearly doesn't match the source, comparing with `#E6DCC8` at the crosshair.
- Render after `renderObjects`, writing depth. Paintings don't cast shadows.

- [ ] **Step 5: Verify every wall**

Run the script and read every frame at full size.
Expected: no old painting edge is visible around any frame, frames are square to the walls, the mat colour looks like paper, and designs aren't stretched. Rope posts and chairs remain. Fix bad rectangles in `painting_rects.json` and regenerate.

- [ ] **Step 6: Measure cost**

Log time from launch to first frame and resident memory using `ps -o rss=`.
Expected: under 5 seconds and under 1.5 GB, with fps at least 50 in the same run.

- [ ] **Step 7: Commit**

```bash
git add src assets/shaders assets/rooms/museum.json tests/scripts/walls.txt
git commit -m "Hang artist paintings over every gallery painting"
```

---

### Task 8: Press E to meet the artist

**Files:**
- Create: `src/ui/TextLayout.h`, `src/ui/TextLayout.cpp`, `src/ui/ArtistView.h`, `src/ui/ArtistView.cpp`, `tests/test_text_layout.cpp`, `tests/scripts/artist_view.txt`
- Modify: `src/scene/Scene.h`, `src/scene/Scene.cpp`, `src/core/TestDriver.cpp`

**Interfaces:**
- Consumes: `pickPainting`, `Painting`, `Artist`, `ArtistCatalog::find`.
- Produces:

```cpp
std::vector<std::string> wrapText(const std::string& text, size_t maxChars);
struct ArtistViewLayout { float imageX, imageY, imageW, imageH, textX, textW, textTopY, nameScale, bodyScale, titleScale; };
ArtistViewLayout computeArtistViewLayout(int screenW, int screenH);
float artistViewTextHeight(const Artist&, const ArtistDesign&, const ArtistViewLayout&);

class ArtistView {
public:
    void open(const Artist& artist, int startDesign);  // loads this artist's full images, frees them on close
    void update(float dt, const InputManager& input);
    void renderUI(UIOverlay& ui, int screenW, int screenH);
    bool isOpen() const;
    int currentPage() const;
    const std::string& artistId() const;
};
```

- [ ] **Step 1: Write failing tests**

```cpp
TEST(wrapKeepsWordsWhole)
TEST(wrapBreaksWordLongerThanLine)
TEST(wrapHandlesEmptyText)
TEST(imageTakesAbout46PercentOfWidth)       // layout at 1280x720: imageW/screenW within 0.44..0.48
TEST(maxLengthTextFitsAt1280x720)           // limits from Task 3: textTopY + height < hint Y
TEST(maxLengthTextFitsAtMinimumWindow)      // the same at 960x540
TEST(pageTurnStopsAtEnds)                   // D on the last page and A on the first stay put
TEST(pageKeysIgnoredWhileOpening)
TEST(opensOnChosenDesign)                   // open(artist, 3): currentPage()==3
```

`ArtistView`'s state logic has to be testable without OpenGL, so keep image loading behind a small seam the tests can skip. Move only that logic, not the drawing, into `TextLayout` or a small struct in `ArtistView.h`.

- [ ] **Step 2: Run to verify they fail**

Expected: fails to compile.

- [ ] **Step 3: Implement layout and `ArtistView`**

Follow option B in `docs/superpowers/specs/2026-11-06-artist-discovery-mockup.html`. Left: the design on the paper colour, not stretched. Right, vertically centred: name in spaced capitals, artist description, large title, design description, then `2 / 6`. Bottom: the exact hint. Use the same 0.4 second fade as `Book`, and reuse its `book_open` and `page_turn` sounds. Load images with `flipVertically` false and `sRGB` false, because the UI draws them directly.

- [ ] **Step 4: Run to verify they pass**

Expected: all pass.

- [ ] **Step 5: Connect it in `Scene`**

- After book proximity, set `m_nearPainting = pickPainting(...)`, skipped while the view is open or the game is paused.
- E opens `m_artistView` on that artist at the painting's `designIndex`. While open, only the view updates, so the player can't walk.
- Prompt: the exact text. Crosshair hidden while open.
- Extend the driver's `state` command with these values.

- [ ] **Step 6: Write and run `tests/scripts/artist_view.txt`**

Aim at a known painting: `state`, `key tap E`, `wait 1`, `state`, `shot view_page`. Then D, A, D past the last page, Q, then W to confirm walking resumes. Also a run with the window resized while open, and one with the crosshair on a gap between frames.

Expected:
- The `state` line shows the painting's artist and design index before and after opening.
- The page number is right after each key and stops at both ends.
- `view=closed` after Q and the position changes after W.
- On a gap, `near=none` and E does nothing.
- `shot view_page` matches option B with the text inside its column at every tested size, and the image is upright and sharp.

- [ ] **Step 7: Commit**

```bash
git add src tests CMakeLists.txt
git commit -m "Open an artist's designs from any painting"
```

---

### Task 9: Whole-gallery check and adding-an-artist proof

**Files:**
- Create: `tests/scripts/every_painting.txt`, generated by `tools/build_paintings.py --driver-script`
- Modify: `src/core/TestDriver.cpp`, `tools/build_paintings.py`, `README.md`, `CLAUDE.md`

- [ ] **Step 1: Generate and run a script visiting every painting**

For each painting, the driver needs a direct way to stand in front of it and aim at its centre. Add a driver command `aim <painting id>` that moves the player to the reachable point nearest the painting, within walkable limits, and sets the look direction. Then `state`, `key tap E`, `wait 0.5`, `state`, `key tap Q`, `wait 0.5`.

Expected: every painting's `near=` is itself, and the view opens on its own artist and design. List any failures. A frame hidden behind a neighbour or unreachable from the floor is a bug to fix in the rectangles or the pick distance.

- [ ] **Step 2: Prove adding an artist needs no code**

In a scratch copy of the build folder's assets, add one artist folder, change one painting's `artist` and `design`, and run without rebuilding.
Expected: that painting shows and opens the new artist, and no other painting changes.

- [ ] **Step 3: Document it**

Add a short "Adding an artist" section to `README.md` and `CLAUDE.md`, covering the folder format, text limits, how to reassign a painting, and the accented-name limit from the spec.

- [ ] **Step 4: Run everything once more**

Run: `ctest --test-dir build-test --output-on-failure && python3 -m unittest tests/test_build_paintings.py && cmake --build build -j8 && ./build/digital_wounds`
Expected: all tests pass, and the normal build launches into the gallery with no errors logged.

- [ ] **Step 5: Commit**

```bash
git add src/core/TestDriver.cpp tests tools README.md CLAUDE.md
git commit -m "Verify every painting opens its artist and document adding artists"
```

-- Vault-specific obsidian.nvim overlay for LazyVim.
--
-- Assumes a stock LazyVim install (blink.cmp for completion, snacks_picker
-- for pickers). Older LazyVim installs may use fzf-lua, which obsidian.nvim
-- also supports.
--
-- Required system packages: ripgrep, wl-clipboard (Wayland) or xclip (X11).
-- On WSL, also install wsl-open for :Obsidian open.
--
-- Set OBSIDIAN_VAULT to override the default vault path (~/vault).
-- render-markdown.lua in this directory is a recommended companion for visual
-- markdown rendering; it is not required by obsidian.nvim.
--
-- ---------------------------------------------------------------------------
-- Deviations from obsidian.nvim defaults (full table and rationale in
-- DESIGN.md §12; the underlying design decisions live in §5, §9, §11):
--
-- Opts that change obsidian.nvim behavior beyond naming the workspace:
--   notes_subdir, new_notes_location   :Obsidian new + [[...]]-follow-
--                                      creating both land in 2-permanent/.
--                                      Rationale: in nvim, extracting
--                                      atomic claims from literature notes
--                                      into permanent is the dominant
--                                      pattern. Fleeting stays the default
--                                      in Obsidian GUI (mobile + desktop).
--   note.template                      Auto-applies permanent.md on
--                                      creation in nvim.
--   templates.folder                   Points at vault's 5-templates/.
--   templates.customizations           Routes each template type (picked
--                                      via <leader>oN or <leader>oM) to
--                                      its content folder (fleeting →
--                                      0-fleeting/, literature →
--                                      1-literature/, etc.).
--   note_id_func                       Slugifies titles → filenames. Slug
--                                      rules documented in DESIGN.md §11.
--   attachments.folder                 Image saves go to 6-assets/.
--   ui.enable = false                  render-markdown.nvim handles visual
--                                      rendering; obsidian.nvim's UI would
--                                      overlap.
--   completion.blink + nvim_cmp        LazyVim ships blink.cmp; match it.
--
-- Vault-specific keybindings (not obsidian.nvim commands):
--   <leader>oS   Slugify note (slug rename + normalize.py --apply)
--   <leader>oM   Promote/move note to a different type (folder move +
--                normalize.py --reapply). Same orchestration split as oS:
--                Lua owns the filesystem action, normalize.py owns body
--                and frontmatter.
--
-- Routine normalization (frontmatter hygiene, H1 insertion, aliases↔H1
-- sync, template body application when body lacks ## headings) runs
-- automatically via the pre-commit hook on every commit; users don't
-- need a keybinding for it. Use <leader>oS when you want the full
-- pipeline in-session (slug rename included).
--
-- Pass-through keybindings to obsidian.nvim native commands. Two
-- groups mirroring the plugin's general-action / note-action split;
-- within each group, alphabetical by the binding letter:
--   General:  <leader>on, oN, oo, os
--   Note:     <leader>ob, ol, op, or, ot
-- Descriptions are the plugin's own shipped strings from
-- lua/obsidian/commands/init-legacy.lua.
-- See the `keys` table below for each one's exact command mapping.
-- ---------------------------------------------------------------------------

vim.g.markdown_folding = 1

-- Map a human title to a slug filename. Five steps (order matters):
--   1. replace spaces with hyphens
--   2. strip any character that is not ASCII alphanumeric or hyphen
--   3. collapse runs of hyphens into one
--   4. strip leading and trailing hyphens
--   5. lowercase
-- Worked examples and known limitations (non-ASCII stripping, punctuation
-- collision) documented in DESIGN.md §11.
local function slugify(title)
  return title:gsub(" ", "-"):gsub("[^A-Za-z0-9-]", ""):gsub("%-+", "-"):gsub("^%-", ""):gsub("%-$", ""):lower()
end

local vault_path = vim.env.OBSIDIAN_VAULT or (vim.env.HOME .. "/vault")

-- Invoke .githooks/lib/normalize.py on a file. mode is "--apply" or
-- "--fill". If target_path is nil, the current buffer is used (saving
-- first). Returns true on success, false on failure or out-of-vault.
local function run_normalize(mode, fallback_alias, target_path)
  local path = target_path or vim.api.nvim_buf_get_name(0)
  if not path:find(vault_path .. "/", 1, true) then
    vim.notify("Not in vault", vim.log.levels.WARN)
    return false
  end

  if not target_path then
    local ok_write = pcall(vim.cmd, "write")
    if not ok_write then
      vim.notify("Could not save buffer", vim.log.levels.ERROR)
      return false
    end
  end

  local cmd = {
    "python3",
    vault_path .. "/.githooks/lib/normalize.py",
    mode,
    "--vault-root", vault_path,
  }
  if fallback_alias then
    vim.list_extend(cmd, { "--fallback-alias", fallback_alias })
  end
  table.insert(cmd, path)

  local result = vim.fn.system(cmd)
  if vim.v.shell_error ~= 0 then
    vim.notify("normalize.py " .. mode .. " failed: " .. result, vim.log.levels.ERROR)
    return false
  end

  vim.cmd("edit!")
  return true
end

return {
  {
    "obsidian-nvim/obsidian.nvim",
    version = "*",
    lazy = true,
    event = {
      "BufReadPre " .. vault_path .. "/**.md",
      "BufNewFile " .. vault_path .. "/**.md",
    },
    cmd = { "Obsidian" },
    dependencies = {
      "nvim-lua/plenary.nvim",
    },
    opts = {
      legacy_commands = false,
      workspaces = {
        {
          name = "vault",
          path = vault_path,
        },
      },
      notes_subdir = "2-permanent",
      new_notes_location = "notes_subdir",
      templates = {
        folder = "5-templates",
        date_format = "%Y-%m-%d",
        time_format = "%H:%M",
        customizations = {
          fleeting = { notes_subdir = "0-fleeting" },
          literature = { notes_subdir = "1-literature" },
          permanent = { notes_subdir = "2-permanent" },
          overview = { notes_subdir = "3-overview" },
          writing = { notes_subdir = "4-writing" },
        },
      },
      note = {
        template = "permanent.md",
      },
      completion = {
        blink = true,
        nvim_cmp = false,
        min_chars = 2,
      },
      ui = {
        enable = false,
      },
      attachments = {
        folder = "6-assets",
      },
      note_id_func = function(title)
        if title ~= nil then
          return slugify(title)
        end
        return tostring(os.time())
      end,
    },
    keys = {
      -- obsidian.nvim pass-through bindings. Two groups mirroring the
      -- plugin's general-action / note-action split; within each group,
      -- alphabetical by the binding letter (lowercase before uppercase
      -- for same-letter pairs). Descriptions are the plugin's own
      -- shipped strings from lua/obsidian/commands/init-legacy.lua.

      -- General
      { "<leader>on", "<cmd>Obsidian new<cr>", desc = "Create a new note" },
      { "<leader>oN", "<cmd>Obsidian new_from_template<cr>", desc = "Create a new note from a template" },
      { "<leader>oo", "<cmd>Obsidian quick_switch<cr>", desc = "Switch notes" },
      { "<leader>os", "<cmd>Obsidian search<cr>", desc = "Search vault" },

      -- Note
      { "<leader>ob", "<cmd>Obsidian backlinks<cr>", desc = "Collect backlinks" },
      { "<leader>ol", "<cmd>Obsidian links<cr>", desc = "Collect all links within the current buffer" },
      { "<leader>op", "<cmd>Obsidian paste_img<cr>", desc = "Paste an image from the clipboard" },
      { "<leader>or", "<cmd>Obsidian rename<cr>", desc = "Rename note and update all references to it" },
      { "<leader>ot", "<cmd>Obsidian template<cr>", desc = "Insert a template" },

      -- oS — Slugify note. Full canonicalization in one keystroke:
      --  1. Slugifies the filename via :Obsidian rename (which rewrites
      --     every [[wikilink]] in the vault).
      --  2. Runs normalize.py --apply, passing the pre-rename stem as
      --     the alias fallback so the readable name survives in
      --     aliases[0] when the body has no H1 yet.
      -- No confirmation prompt: if you press the key, you want the slug.
      -- Target-collision check still aborts with an error.
      -- Invariants preserved: id = new filename stem; aliases[1..]
      -- user-added synonyms are kept; H1 reconciled with aliases[0].
      {
        "<leader>oS",
        function()
          local old_path = vim.api.nvim_buf_get_name(0)
          if not old_path:find(vault_path .. "/", 1, true) then
            vim.notify("Not in vault", vim.log.levels.WARN)
            return
          end

          local stem = vim.fn.fnamemodify(old_path, ":t:r")
          local slug = slugify(stem)

          if slug == "" then
            vim.notify("Slug is empty after sanitizing", vim.log.levels.ERROR)
            return
          end

          local ok_write = pcall(vim.cmd, "write")
          if not ok_write then
            vim.notify("Could not save buffer", vim.log.levels.ERROR)
            return
          end

          local final_path = old_path
          local renamed = false

          if stem ~= slug then
            local dir = vim.fn.fnamemodify(old_path, ":h")
            local target = dir .. "/" .. slug .. ".md"
            if vim.fn.filereadable(target) == 1 then
              vim.notify("Target already exists: " .. slug .. ".md", vim.log.levels.ERROR)
              return
            end

            local ok_rename, err = pcall(vim.cmd, "Obsidian rename " .. slug)
            if not ok_rename then
              vim.notify("Rename failed: " .. tostring(err), vim.log.levels.ERROR)
              return
            end
            final_path = vim.api.nvim_buf_get_name(0)
            renamed = true
            pcall(vim.cmd, "write")
          end

          local fallback = nil
          if renamed then
            fallback = stem
          end
          if not run_normalize("--apply", fallback, final_path) then
            return
          end

          if renamed then
            vim.notify("Slugified: " .. stem .. " -> " .. slug .. ".md", vim.log.levels.INFO)
          else
            vim.notify("Note canonicalized (filename already slug)", vim.log.levels.INFO)
          end
        end,
        desc = "Slugify and normalize note",
      },
    },
  },
}

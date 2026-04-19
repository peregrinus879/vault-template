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

vim.g.markdown_folding = 1

local function slugify(title)
  return title:gsub(" ", "-"):gsub("[^A-Za-z0-9-]", ""):gsub("%-+", "-"):gsub("^%-", ""):gsub("%-$", ""):lower()
end

local vault_path = vim.env.OBSIDIAN_VAULT or (vim.env.HOME .. "/vault")

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
      notes_subdir = "0-fleeting",
      new_notes_location = "notes_subdir",
      templates = {
        folder = "5-templates",
        date_format = "%Y-%m-%d",
        time_format = "%H:%M",
        customizations = {
          literature = { notes_subdir = "1-literature" },
          permanent = { notes_subdir = "2-permanent" },
          overview = { notes_subdir = "3-overview" },
          writing = { notes_subdir = "4-writing" },
        },
      },
      note = {
        template = "fleeting.md",
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
      { "<leader>on", "<cmd>Obsidian new<cr>", desc = "New note" },
      { "<leader>oN", "<cmd>Obsidian new_from_template<cr>", desc = "New from template" },
      { "<leader>oo", "<cmd>Obsidian quick_switch<cr>", desc = "Find note" },
      { "<leader>os", "<cmd>Obsidian search<cr>", desc = "Search vault" },
      { "<leader>ob", "<cmd>Obsidian backlinks<cr>", desc = "Backlinks" },
      { "<leader>ot", "<cmd>Obsidian template<cr>", desc = "Insert template" },
      { "<leader>ol", "<cmd>Obsidian links<cr>", desc = "Links" },
      { "<leader>op", "<cmd>Obsidian paste_img<cr>", desc = "Paste image" },
      -- Slug rename orchestrator. Delegates the filename rename and
      -- vault-wide [[wikilink]] rewrite to :Obsidian rename, then runs
      -- .githooks/lib/normalize.py to fill any missing frontmatter.
      -- Backlinks are updated correctly; frontmatter rules are shared
      -- with the pre-commit hook (single source of truth).
      {
        "<leader>or",
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

          -- Save current buffer so disk reflects the latest edits
          -- before any external tool reads the file.
          local ok_write = pcall(vim.cmd, "write")
          if not ok_write then
            vim.notify("Could not save buffer", vim.log.levels.ERROR)
            return
          end

          local final_path = old_path

          if stem ~= slug then
            local dir = vim.fn.fnamemodify(old_path, ":h")
            local target = dir .. "/" .. slug .. ".md"
            if vim.fn.filereadable(target) == 1 then
              vim.notify("Target already exists: " .. slug .. ".md", vim.log.levels.ERROR)
              return
            end

            local choice = vim.fn.confirm(
              "Rename to " .. slug .. ".md and update backlinks?",
              "&Yes\n&No", 2
            )
            if choice ~= 1 then return end

            -- :Obsidian rename renames the file and rewrites every
            -- [[wikilink]] in the vault that targets this note.
            local ok_rename, err = pcall(vim.cmd, "Obsidian rename " .. slug)
            if not ok_rename then
              vim.notify("Rename failed: " .. tostring(err), vim.log.levels.ERROR)
              return
            end
            final_path = vim.api.nvim_buf_get_name(0)
            pcall(vim.cmd, "write")
          end

          local normalize = vault_path .. "/.githooks/lib/normalize.py"
          local result = vim.fn.system({
            "python3", normalize, "--fill",
            "--vault-root", vault_path, final_path,
          })
          if vim.v.shell_error ~= 0 then
            vim.notify("normalize.py failed: " .. result, vim.log.levels.ERROR)
            return
          end

          -- Reload so the buffer reflects normalize.py's disk changes.
          vim.cmd("edit!")

          if stem == slug then
            vim.notify("Frontmatter normalized", vim.log.levels.INFO)
          else
            vim.notify("Renamed: " .. stem .. " -> " .. slug .. ".md", vim.log.levels.INFO)
          end
        end,
        desc = "Rename note to slug",
      },
    },
  },
}

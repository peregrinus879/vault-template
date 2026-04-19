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
      -- Slug rename uses vim.fn.rename(), not :Obsidian rename. Old title is preserved
      -- as an alias; both Obsidian and obsidian.nvim resolve [[wiki-links]] via aliases.
      -- Upstream rename rewrites backlink text vault-wide, unnecessary for normalization.
      -- Limitation: path-based markdown links [text](file.md) are not updated.
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

          if stem == slug then
            vim.notify("Filename already matches slug", vim.log.levels.INFO)
            return
          end

          local dir = vim.fn.fnamemodify(old_path, ":h")
          local new_path = dir .. "/" .. slug .. ".md"

          if vim.fn.filereadable(new_path) == 1 then
            vim.notify("Target already exists: " .. slug .. ".md", vim.log.levels.ERROR)
            return
          end

          local ok = vim.fn.confirm("Rename to " .. slug .. ".md?", "&Yes\n&No", 2)
          if ok ~= 1 then return end

          local lines = vim.api.nvim_buf_get_lines(0, 0, -1, false)
          local new_lines = {}

          if lines[1] == "---" then
            local in_fm = false
            local found_aliases = false
            local found_type = false
            local found_created = false
            local found_updated = false
            local found_tags = false
            local i = 1
            while i <= #lines do
              local line = lines[i]
              if i == 1 and line == "---" then
                in_fm = true
                new_lines[#new_lines + 1] = line
              elseif in_fm and line == "---" then
                if not found_aliases then
                  new_lines[#new_lines + 1] = "aliases:"
                  new_lines[#new_lines + 1] = "  - " .. stem
                end
                if not found_type then
                  new_lines[#new_lines + 1] = "type:"
                end
                if not found_created then
                  new_lines[#new_lines + 1] = "created: " .. os.date("%Y-%m-%d")
                end
                if not found_updated then
                  new_lines[#new_lines + 1] = "updated:"
                end
                if not found_tags then
                  new_lines[#new_lines + 1] = "tags: []"
                end
                in_fm = false
                new_lines[#new_lines + 1] = line
              elseif in_fm and line:match("^id:") then
                new_lines[#new_lines + 1] = "id: " .. slug
                while i + 1 <= #lines and lines[i + 1]:match("^%s") do
                  i = i + 1
                end
              elseif in_fm and line:match("^type:") then
                found_type = true
                new_lines[#new_lines + 1] = line
              elseif in_fm and line:match("^created:") then
                found_created = true
                new_lines[#new_lines + 1] = line
              elseif in_fm and line:match("^updated:") then
                found_updated = true
                new_lines[#new_lines + 1] = line
              elseif in_fm and line:match("^tags:") then
                found_tags = true
                new_lines[#new_lines + 1] = line
              elseif in_fm and line:match("^aliases:") then
                local rest = line:match("^aliases:%s*(.*)$")
                if rest and rest ~= "" and rest ~= "[]" then
                  vim.notify("Inline aliases not supported by slug rename; convert to block style first", vim.log.levels.WARN)
                  return
                end
                found_aliases = true
                new_lines[#new_lines + 1] = "aliases:"
                local existing = {}
                while i + 1 <= #lines and lines[i + 1]:match("^%s+%-") do
                  i = i + 1
                  local val = lines[i]:match("^%s+-%s+(.*)")
                  if val and val ~= "" and val:lower() ~= "untitled" then
                    existing[#existing + 1] = val
                  end
                end
                local has_stem = false
                for _, v in ipairs(existing) do
                  if v == stem then has_stem = true end
                end
                if not has_stem then
                  new_lines[#new_lines + 1] = "  - " .. stem
                end
                for _, v in ipairs(existing) do
                  new_lines[#new_lines + 1] = "  - " .. v
                end
              else
                new_lines[#new_lines + 1] = line
              end
              i = i + 1
            end
          else
            vim.list_extend(new_lines, {
              "---",
              "id: " .. slug,
              "aliases:",
              "  - " .. stem,
              "type:",
              "created: " .. os.date("%Y-%m-%d"),
              "updated:",
              "tags: []",
              "---",
            })
            vim.list_extend(new_lines, lines)
          end

          if vim.fn.rename(old_path, new_path) ~= 0 then
            vim.notify("Rename failed", vim.log.levels.ERROR)
            return
          end
          vim.api.nvim_buf_set_lines(0, 0, -1, false, new_lines)
          vim.api.nvim_buf_set_name(0, new_path)
          vim.cmd("write!")
          vim.notify("Renamed: " .. stem .. " -> " .. slug .. ".md", vim.log.levels.INFO)
        end,
        desc = "Rename note to slug",
      },
    },
  },
}

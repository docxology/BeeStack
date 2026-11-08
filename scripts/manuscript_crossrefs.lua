-- Resolve manuscript cross-references before citeproc; unknown targets fail closed.
function Pandoc(doc)
  local targets = {}
  local figure = 0
  doc:walk({
    Header = function(el)
      if el.identifier ~= "" then targets[el.identifier] = pandoc.utils.stringify(el.content) end
    end,
    Figure = function(el)
      if el.identifier ~= "" then
        figure = figure + 1
        targets[el.identifier] = "Figure " .. figure
      end
    end,
    Image = function(el)
      if el.identifier ~= "" then
        figure = figure + 1
        targets[el.identifier] = "Figure " .. figure
      end
    end
  })
  return doc:walk({
    Code = function(el)
      -- Break literal artifact paths/commands without losing monospaced provenance.
      if FORMAT:match("latex") and el.text:match("^[%w_./%* %-]+$") and el.text:find("[/_]") then
        return pandoc.RawInline("latex", "\\path|" .. el.text .. "|")
      end
    end,
    Cite = function(el)
      local crossrefs = false
      for _, citation in ipairs(el.citations) do
        if (citation.id:match("^fig:") or citation.id:match("^sec:") or citation.id:match("^eq:") or citation.id:match("^tbl:")) then crossrefs = true end
      end
      if not crossrefs then return nil end
      local result = pandoc.List()
      for index, citation in ipairs(el.citations) do
        if index > 1 then result:insert(pandoc.Str(";")); result:insert(pandoc.Space()) end
        local label = targets[citation.id]
        if not label then error("Unknown or mixed manuscript cross-reference: " .. citation.id) end
        result:insert(pandoc.Link({pandoc.Str(label)}, "#" .. citation.id))
      end
      return result
    end
  })
end

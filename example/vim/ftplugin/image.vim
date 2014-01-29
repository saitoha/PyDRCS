if !has('gui_running')
    function! s:ViewImage()
        if &ambiwidth == 'single'
            setlocal nowrap
            setlocal foldlevel=0
            setlocal foldmethod=marker
            setlocal foldmarker=P,\
            %delete
            call system('cat "' . expand('%:p') . '" | drcsconv -u --ncolor=256 > /tmp/drcs')
            let lines = readfile('/tmp/drcs')
            call append(0, lines)
            call filter(lines, 'len(v:val) > 0 && char2nr(v:val[0]) < 128')
            call writefile(lines, '/dev/tty', 'b')
            call cursor(len(lines) + 1, 0)
            call feedkeys("z\<CR>")
        endif
    endfunction
    
    autocmd! TermResponse * call s:ViewImage()
    if len(v:termresponse) 
        call s:ViewImage()
    endif
endif

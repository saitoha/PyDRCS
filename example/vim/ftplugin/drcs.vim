autocmd! TermResponse *.drcs setlocal ambiwidth=single
setlocal ambiwidth=single
setlocal nowrap
setlocal foldlevel=0
setlocal foldmethod=marker
setlocal foldmarker=P,\
let lines = getline(0,'$')
call filter(lines, 'len(v:val) > 0 && char2nr(v:val[0]) < 128')
call insert(lines, "\e[?8428h", 0)
call writefile(lines, '/dev/tty', 'b')
call cursor(len(lines), 0)
call feedkeys("z\<CR>")

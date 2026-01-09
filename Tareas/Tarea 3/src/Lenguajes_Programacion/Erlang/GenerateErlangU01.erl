#!/usr/bin/env escript
%%! -noshell

main(Args) ->
    Out  = get_arg(Args, 1, "erlang_u01.txt"),
    N    = list_to_integer(get_arg(Args, 2, "1000000")),
    Seed = list_to_integer(get_arg(Args, 3, "123456789")),

    rand:seed(exsplus, {Seed, Seed bxor 16#DEADBEEF, Seed + 1}),

    {ok, Fd} = file:open(Out, [write, raw, {delayed_write, 1024*1024, 2000}]),
    Base = 1 bsl 53,     % para obtener [0,1) con pasos 2^-53
    Chunk = 10000,

    gen_chunks(Fd, N, Base, Chunk),
    file:close(Fd),

    io:format("Listo: ~p numeros en [0,1) -> ~s (seed=~p)~n", [N, Out, Seed]),
    ok.

get_arg(Args, Pos, Default) ->
    case length(Args) >= Pos of
        true  -> lists:nth(Pos, Args);
        false -> Default
    end.

gen_chunks(_Fd, 0, _Base, _Chunk) -> ok;
gen_chunks(Fd, N, Base, Chunk) ->
    M = if N < Chunk -> N; true -> Chunk end,
    Lines = make_lines(M, Base, []),
    ok = file:write(Fd, Lines),
    gen_chunks(Fd, N - M, Base, Chunk).

make_lines(0, _Base, Acc) -> lists:reverse(Acc);
make_lines(K, Base, Acc) ->
    I = rand:uniform(Base) - 1,    % 0..Base-1
    X = I / Base,                 % [0,1)
    Bin = float_to_binary(X, [{decimals, 16}]),
    make_lines(K - 1, Base, [[Bin, "\n"] | Acc]).

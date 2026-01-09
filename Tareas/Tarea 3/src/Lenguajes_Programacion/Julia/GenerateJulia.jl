# Genera números reales uniformes en [0,1) y los guarda en un archivo
function generar_u01_archivo(nombre_archivo, cantidad)
    open(nombre_archivo, "w") do io
        for _ in 1:cantidad
            println(io, rand())
        end
    end
end

n = 1_000_000
generar_u01_archivo("julia_u01.txt", n)

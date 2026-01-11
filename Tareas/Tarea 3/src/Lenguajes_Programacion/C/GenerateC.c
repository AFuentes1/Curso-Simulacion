#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define OUT_DIR "src/Lenguajes_Programacion/C"

int uniforme_discreto(int k) {
    int r, limite = RAND_MAX - (RAND_MAX % k);
    do { r = rand(); } while (r >= limite);
    return (r % k) + 1;
}

int main(void) {
    const int n = 1000000;
    srand((unsigned)time(NULL));

    FILE *f1 = fopen(OUT_DIR "/c_u1_4.txt", "w");
    FILE *f2 = fopen(OUT_DIR "/c_u1_8.txt", "w");

    if (!f1 || !f2) {
        printf("Error: no pude crear los archivos en %s\n", OUT_DIR);
        if (f1) fclose(f1);
        if (f2) fclose(f2);
        return 1;
    }

    for (int i = 0; i < n; i++) fprintf(f1, "%d\n", uniforme_discreto(4));
    for (int i = 0; i < n; i++) fprintf(f2, "%d\n", uniforme_discreto(8));

    fclose(f1); fclose(f2);
    printf("Listo: creados %s/c_u1_4.txt y %s/c_u1_8.txt\n", OUT_DIR, OUT_DIR);
    return 0;
}
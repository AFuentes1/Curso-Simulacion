#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int uniforme_discreto(int k) {
    int r, limite;
    limite = RAND_MAX - (RAND_MAX % k);

    do {
        r = rand();
    } while (r >= limite);

    return (r % k) + 1;
}

int main(void) {
    int n = 1000000;
    int i;

    FILE *f1;
    FILE *f2;

    srand(time(NULL));

    f1 = fopen("c_u1_4.txt", "w");
    f2 = fopen("c_u1_8.txt", "w");

    if (!f1 || !f2) {
        printf("Error abriendo archivos\n");
        return 1;
    }

    /* {1,2,3,4} */
    for (i = 0; i < n; i++) {
        fprintf(f1, "%d\n", uniforme_discreto(4));
    }

    /* {1,2,3,4,5,6,7,8} */
    for (i = 0; i < n; i++) {
        fprintf(f2, "%d\n", uniforme_discreto(8));
    }

    fclose(f1);
    fclose(f2);

    return 0;
}

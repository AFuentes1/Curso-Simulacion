import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.SplittableRandom;

public class GenerateJavaU01 {
    public static void main(String[] args) {
        String outFile = (args.length >= 1) ? args[0] : "java_u01.txt";
        int n = (args.length >= 2) ? Integer.parseInt(args[1]) : 1_000_000;
        long seed = (args.length >= 3) ? Long.parseLong(args[2]) : 123456789L;

        SplittableRandom rng = new SplittableRandom(seed);

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(outFile))) {
            for (int i = 0; i < n; i++) {
                // nextDouble() genera en [0.0, 1.0)
                double x = rng.nextDouble();
                bw.write(Double.toString(x));
                bw.newLine();
            }
            System.out.println("Listo: " + n + " numeros en [0,1) -> " + outFile + " (seed=" + seed + ")");
        } catch (IOException e) {
            System.err.println("Error escribiendo archivo: " + e.getMessage());
        }
    }
}

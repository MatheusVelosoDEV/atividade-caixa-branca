import java.nio.file.Path;

/** Exemplo de linha de comando para a versão revisada. */
public class Main {
    public static void main(String[] args) throws Exception {
        if (args.length < 4 || ("saida".equals(args[2]) && args.length != 5)) {
            System.err.println("Uso: java Main <estoque.csv> <movimentacoes.txt> consulta|saida <codigo> [quantidade]");
            System.exit(2);
        }
        EstoqueArquivo estoque = new EstoqueArquivo(Path.of(args[0]), Path.of(args[1]));
        if ("consulta".equals(args[2])) {
            System.out.println(estoque.consultarQuantidade(args[3]));
        } else if ("saida".equals(args[2])) {
            System.out.println(estoque.registrarSaida(args[3], Integer.parseInt(args[4])));
        } else {
            throw new IllegalArgumentException("Operação deve ser consulta ou saida");
        }
    }
}

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

/** Acesso simples a um estoque CSV de duas colunas: codigo;quantidade. */
public class EstoqueArquivo {
    private final Path arquivoEstoque;
    private final Path arquivoMovimentacoes;
    private String ultimaMovimentacao = "";

    public EstoqueArquivo(Path arquivoEstoque, Path arquivoMovimentacoes) {
        if (arquivoEstoque == null || arquivoMovimentacoes == null) {
            throw new IllegalArgumentException("Os caminhos dos arquivos são obrigatórios");
        }
        this.arquivoEstoque = arquivoEstoque;
        this.arquivoMovimentacoes = arquivoMovimentacoes;
    }

    public int consultarQuantidade(String codigo) throws IOException {
        validarCodigo(codigo);
        try (BufferedReader leitor = Files.newBufferedReader(arquivoEstoque, StandardCharsets.UTF_8)) {
            String linha;
            int numeroLinha = 0;
            while ((linha = leitor.readLine()) != null) {
                numeroLinha++;
                String[] colunas = linha.split(";", -1);
                if (colunas.length != 2 || colunas[0].isBlank()) {
                    throw new IOException("CSV inválido na linha " + numeroLinha);
                }
                final int quantidade;
                try {
                    quantidade = Integer.parseInt(colunas[1]);
                } catch (NumberFormatException e) {
                    throw new IOException("Quantidade inválida na linha " + numeroLinha, e);
                }
                if (quantidade < 0) {
                    throw new IOException("Quantidade negativa na linha " + numeroLinha);
                }
                if (colunas[0].equals(codigo)) {
                    return quantidade;
                }
            }
            return 0;
        }
    }

    /** Registra a saída; o CSV de estoque permanece uma fonte de consulta. */
    public synchronized boolean registrarSaida(String codigo, int quantidade) throws IOException {
        validarCodigo(codigo);
        if (quantidade <= 0) {
            throw new IllegalArgumentException("A quantidade de saída deve ser positiva");
        }
        int disponivel = consultarQuantidade(codigo);
        if (quantidade > disponivel) {
            return false;
        }
        try (BufferedWriter escrita = Files.newBufferedWriter(arquivoMovimentacoes,
                StandardCharsets.UTF_8, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            escrita.write(codigo + ";" + quantidade);
            escrita.newLine();
        }
        ultimaMovimentacao = codigo;
        return true;
    }

    public synchronized String getUltimaMovimentacao() {
        return ultimaMovimentacao;
    }

    private static void validarCodigo(String codigo) {
        if (codigo == null || codigo.isBlank() || codigo.contains(";")
                || codigo.contains("\n") || codigo.contains("\r")) {
            throw new IllegalArgumentException("Código inválido");
        }
    }
}

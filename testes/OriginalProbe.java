public class OriginalProbe {
    public static void main(String[] args) {
        EstoqueArquivo estoque = new EstoqueArquivo();
        String codigo = "NULL".equals(args[1]) ? null : args[1];
        try {
            if ("consulta".equals(args[0])) {
                System.out.println("RET=" + estoque.consultarQuantidade(codigo));
            } else {
                System.out.println("RET=" + estoque.registrarSaida(codigo, Integer.parseInt(args[2])));
            }
        } catch (Exception e) {
            System.out.println("EX=" + e.getClass().getSimpleName());
        }
        System.out.println("ULTIMA=" + estoque.getUltimaMovimentacao());
    }
}

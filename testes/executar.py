"""Compila as duas versões isoladamente e registra observações reproduzíveis."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

CASES = [
    # id, versão, operação, código, quantidade, CSV, destino, esperado, última, arquivo
    ("O01", "original", "consulta", "A", 0, "A;7\nB;2\n", "none", "RET=7", "", None),
    ("O02", "original", "consulta", "Z", 0, "A;7\n", "none", "RET=0", "", None),
    ("O03", "original", "consulta", "A", 0, None, "none", "RET=0", "", None),
    ("O04", "original", "consulta", "A", 0, "A;abc\n", "none", "EX=NumberFormatException", "", None),
    ("O05", "original", "consulta", "A", 0, "A\n", "none", "EX=ArrayIndexOutOfBoundsException", "", None),
    ("O06", "original", "saida", "A", 3, "A;7\n", "none", "RET=true", "A", ""),
    ("O07", "original", "saida", "A", 8, "A;7\n", "none", "RET=false", "", None),
    ("O08", "original", "saida", "A", -2, "A;7\n", "none", "RET=true", "A", ""),
    ("O09", "original", "saida", "A", 1, "A;7\n", "directory", "RET=false", "", None),
    ("O10", "original", "saida", "A", 1, "A;abc\n", "none", "EX=NumberFormatException", "", None),
    ("O11", "original", "saida", "A", 0, "A;7\n", "none", "RET=true", "A", ""),
    ("R01", "revisado", "consulta", "A", 0, "A;7\nB;2\n", "none", "RET=7", "", None),
    ("R02", "revisado", "consulta", "Z", 0, "A;7\n", "none", "RET=0", "", None),
    ("R03", "revisado", "consulta", "A", 0, None, "none", "EX=NoSuchFileException", "", None),
    ("R04", "revisado", "consulta", "A", 0, "A;abc\n", "none", "EX=IOException", "", None),
    ("R05", "revisado", "consulta", "A", 0, "A\n", "none", "EX=IOException", "", None),
    ("R06", "revisado", "saida", "A", 3, "A;7\n", "none", "RET=true", "A", "A;3\n"),
    ("R07", "revisado", "saida", "A", 8, "A;7\n", "none", "RET=false", "", None),
    ("R08", "revisado", "saida", "A", -2, "A;7\n", "none", "EX=IllegalArgumentException", "", None),
    ("R09", "revisado", "saida", "A", 0, "A;7\n", "none", "EX=IllegalArgumentException", "", None),
    ("R10", "revisado", "saida", "A", 1, "A;7\n", "directory", "EX=AccessDeniedException|EX=FileSystemException", "", None),
    ("R11", "revisado", "saida", "NULL", 1, "A;7\n", "none", "EX=IllegalArgumentException", "", None),
    ("R12", "revisado", "saida", "A", 7, "A;7\n", "none", "RET=true", "A", "A;7\n"),
    ("R13", "revisado", "consulta", "A", 0, "B;abc\nA;7\n", "none", "EX=IOException", "", None),
    ("R14", "revisado", "saida", "A", 1, "A;abc\n", "none", "EX=IOException", "", None),
]


def main():
    lines = ["Comando: python testes/executar.py", "Java e Python: versões locais; arquivos em diretórios temporários."]
    failures = []
    with tempfile.TemporaryDirectory(prefix="caixa-branca-") as temp:
        temp = Path(temp)
        builds = {}
        for version, probe in (("original", "OriginalProbe"), ("revisado", "RevisadoProbe")):
            build = temp / ("classes-" + version)
            build.mkdir()
            cmd = ["javac", "-encoding", "UTF-8", "-d", str(build),
                   str(ROOT / version / "EstoqueArquivo.java"), str(ROOT / "testes" / (probe + ".java"))]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            builds[version] = (build, probe)
        for case_id, version, operation, codigo, quantidade, csv, destination, expected, last, expected_file in CASES:
            work = temp / case_id
            work.mkdir()
            if csv is not None:
                (work / "estoque.csv").write_text(csv, encoding="utf-8")
            if destination == "directory":
                (work / "movimentacoes.txt").mkdir()
            build, probe = builds[version]
            cmd = ["java", "-cp", str(build), probe, operation, codigo, str(quantidade)]
            run = subprocess.run(cmd, cwd=work, capture_output=True, text=True, check=True)
            observed = run.stdout.strip().splitlines()
            movement = work / "movimentacoes.txt"
            file_value = movement.read_text(encoding="utf-8") if movement.is_file() else None
            ok = any(choice in observed for choice in expected.split("|")) and f"ULTIMA={last}" in observed and file_value == expected_file
            if not ok:
                failures.append(case_id)
            status = "PASSOU" if ok else "FALHOU"
            lines.append(f"{case_id} {status} | esperado={expected}, ULTIMA={last!r}, arquivo={expected_file!r} | observado={observed!r}, arquivo={file_value!r}")
    lines.append(f"Total: {len(CASES) - len(failures)}/{len(CASES)} verificações de observação passaram.")
    lines.append("Observação: O03, O06, O08 e O11 reproduzem defeitos funcionais do original apesar de a observação passar.")
    output = "\n".join(lines) + "\n"
    evidence = ROOT / "evidencias" / "execucao.txt"
    evidence.parent.mkdir(exist_ok=True)
    evidence.write_text(output, encoding="utf-8")
    print(output, end="")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()

def Pascal_Code_Checker(code, input, output, name):
    import subprocess
    import os

    Compiler_Folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Compiler_Folder'))
    pure_filename = f"solution_{name}.pas"
    pure_exe_filename = f"solution_{name}.exe"
    filename = os.path.join(Compiler_Folder, pure_filename)
    exe_filename = os.path.join(Compiler_Folder, pure_exe_filename)
    os.makedirs(Compiler_Folder, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        compile_code = subprocess.run(
            ["mono", "pabcnetc.exe", pure_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            cwd=Compiler_Folder
        )

        if compile_code.returncode != 0:
            return False, 'Произошла ошибка компиляции!', f'Ошибка компиляции:\n{compile_code.stderr}'

        for index, (code_input, expect_output) in enumerate(zip(input, output), start=1):
            try:
                run_code = subprocess.run(
                    ["mono", pure_exe_filename],
                    input=code_input,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True,
                    timeout=1,
                    cwd=Compiler_Folder
                )

                if run_code.returncode != 0:
                    return False, 'Ошибка выполнения программы!', f"Ошибка выполнения на тесте {index}:\n{run_code.stderr}"

                student_answer = run_code.stdout.strip()
                right_answer = expect_output.strip()
                if student_answer != right_answer:
                    return False, 'Задача решена неверно', f'Решение неверное.\nОжидалось: "{right_answer}", получено: {student_answer}'
            except subprocess.TimeoutExpired:
                return False, 'Время истекло', None
        return True, 'Правильно!'
    except Exception as error:
        return False, "Внутрення ошибка сервера! Попробуйте позже!", None

    finally:
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(exe_filename):
            os.remove(exe_filename)
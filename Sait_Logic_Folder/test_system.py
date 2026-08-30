def Pascal_Code_Checker(code, input, output, name):
    import subprocess
    import os

    Solution_Folder_Direction = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data_Folder', 'Solutions_Folder'))
    filename = os.path.join(Solution_Folder_Direction, f"solution_{name}.pas")
    exe_filename = os.path.join(Solution_Folder_Direction, f"solution_{name}.exe")
    os.makedirs(Solution_Folder_Direction, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        compiler_path = os.path.abspath(os.path.join(Solution_Folder_Direction, '..', '..', 'Compiler_Folder', 'pabcnetc.exe'))
        compiler_dir = os.path.dirname(compiler_path)
        compile_code = subprocess.run(
            ["mono", compiler_path, os.path.abspath(filename)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            cwd=compiler_dir
        )

        if compile_code.returncode != 0:
            return False, 'Произошла ошибка компиляции!', f'Ошибка компиляции:\n{compile_code.stderr}'

        for index, (code_input, expect_output) in enumerate(zip(input, output), start=1):
            try:
                run_code = subprocess.run(
                    ["mono", os.path.abspath(exe_filename)],
                    input=code_input,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True,
                    timeout=1,
                    cwd=Solution_Folder_Direction
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
        print(error)
        return False, "Внутрення ошибка сервера на стороне компилятора", None

    finally:
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(exe_filename):
            os.remove(exe_filename)
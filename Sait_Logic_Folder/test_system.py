def Pascal_Code_Checker(code, input: list, output: list, name: str):
    import subprocess
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    compiler_path = os.path.join(os.path.abspath(os.path.join(current_dir, "..")), "Compiler_Folder", "pabcnetc.dll")

    file_name = f"{name}.pas"
    exe_file = f"{name}.exe"

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        compile_process = subprocess.run(
            ["dotnet", compiler_path, file_name],
            input="\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            timeout=5
        )
    except subprocess.TimeoutExpired:
        return False, "Время ожидания истекло!", None
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

    if not os.path.exists(exe_file):
        return False, "Ошибка на стороне сервера. Попробуйте позже!", None

    try:
        for index in range(len(output)):
            
            
            if index < len(input):
                string_input = str(input[index]).strip() + "\n"
            else:
                string_input = "\n" 
                
            code_out = output[index]

            run_process = subprocess.Popen(
                ["dotnet", exe_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            ) 

            try:    
                stdout, stdeer = run_process.communicate(input=string_input, timeout=1)

                if run_process.returncode != 0:
                    return False, "Ошибка выполнения программы!", f"Ошибка на тесте: {index+1}.\n Ощибка:\n {stdeer}" 

                if stdout.strip() != str(code_out).strip():
                    return False, "Задача решена неверно!", f"На тесте {index+1} допущена ошибка. \n Ожидалось: '{str(code_out).strip()}', \nПолучено: '{stdout.strip()}'"
                else:
                    return True, "Правильное решение!", True
            
            except subprocess.TimeoutExpired:
                run_process.kill()
                run_process.communicate()
                return False, "Время ожидания истекло!", None
    
    except Exception as e:
        return False, "Внутренняя ошибка сервера. Попробуйте позже!", str(e)

    finally:
        if os.path.exists(exe_file):
            os.remove(exe_file)
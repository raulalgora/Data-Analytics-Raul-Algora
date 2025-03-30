import luigi
import os
import subprocess

class ExecuteBBBDScripts(luigi.Task):
    """
    Tarea para ejecutar todos los scripts dentro de la carpeta BBDD.
    Cada script creará una tabla en la base de datos PostgreSQL.
    """
    bbdd_dir = "BBDD"

    def output(self):
        return luigi.LocalTarget("logs/bbdd_scripts_done.txt")

    def run(self):
        # Asegúrate de que exista la carpeta de logs
        os.makedirs("logs", exist_ok=True)
        
        # Obtener todos los archivos .py en la carpeta BBDD
        bbdd_files = [f for f in os.listdir(self.bbdd_dir) if f.endswith(".py")]

        for script in bbdd_files:
            script_path = os.path.join(self.bbdd_dir, script)
            print(f"Ejecutando script: {script_path}")
            subprocess.check_call(["python", script_path])

        # Marca la tarea como completada escribiendo en el archivo de salida
        with self.output().open("w") as f:
            f.write("Todos los scripts de BBDD se ejecutaron correctamente.")

class ExecutePostgresQuery(luigi.Task):
    """
    Tarea para ejecutar query.py después de haber ejecutado todos los scripts de BBDD.
    """
    query_script = "POSTGRES/query.py"

    def requires(self):
        return ExecuteBBBDScripts()

    def output(self):
        return luigi.LocalTarget("logs/query_script_done.txt")

    def run(self):
        print(f"Ejecutando script: {self.query_script}")
        subprocess.check_call(["python", self.query_script])

        # Marca la tarea como completada
        with self.output().open("w") as f:
            f.write("El script query.py se ejecutó correctamente.")

if __name__ == "__main__":
    luigi.build([ExecutePostgresQuery()], local_scheduler=True)

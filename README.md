https://roadmap.sh/projects/task-tracker
# Task Tracker CLI Project {Proyecto de CLI para Seguimiento de Tareas}

Build a CLI app to track your tasks and manage your to-do list.  
{Construye una aplicación de interfaz de línea de comandos para trackear (seguir) tus tareas y gestionar tu lista de pendientes.}

## Overview {Resumen}

Task tracker is a project used to track and manage your tasks. In this task, you will build a simple command line interface (CLI) to track what you need to do, what you have done, and what you are currently working on. This project will help you practice your programming skills, including working with the filesystem, handling user inputs, and building a simple CLI application.
{Task tracker es un proyecto para seguir y gestionar tareas. Construirás una CLI simple para rastrear qué necesitas hacer, qué has hecho y en qué estás trabajando actualmente. Este proyecto te ayudará a practicar habilidades como: manejo del sistema de archivos, gestión de entradas de usuario y construcción de aplicaciones CLI.}

## Requirements {Requerimientos}

The application should run from the command line, accept user actions and inputs as arguments, and store the tasks in a JSON file. The user should be able to:
{La aplicación debe ejecutarse desde la línea de comandos, aceptar acciones y entradas del usuario como argumentos, y almacenar las tareas en un archivo JSON. El usuario debe poder:}

- **Add** {Agregar}, **Update** {Actualizar}, and **Delete** {Eliminar} tasks {tareas}.
- **Mark** {Marcar} a task as **in-progress** {en progreso} or **done** {terminada}.
- **List** {Listar} all tasks {todas las tareas}.
- **List** all tasks that are **done**.
- **List** all tasks that are not **done** (status: **todo**).
- **List** all tasks that are **in-progress**.

### Constraints {Restricciones / Limitaciones}

- Use **positional arguments** {argumentos posicionales} in command line to accept user inputs.
- Use a **JSON file** to store the tasks in the current directory.
- The JSON file should be created if it does not exist.
- Use the **native file system module** {módulo nativo del sistema de archivos} of your programming language.
- **Do not use any external libraries or frameworks** {No usar librerías o frameworks externos} to build this project.
- Ensure to handle errors and **edge cases** {casos borde} gracefully.

### Task Properties {Propiedades de la Tarea}

Each task should have the following properties:
{Cada tarea debe tener las siguientes propiedades:}

- **id**: A unique identifier for the task {Un identificador único para la tarea}.
- **description**: A short description of the task {Una descripción corta de la tarea}.
- **status**: The status of the task (**todo**, **in-progress**, **done**).
- **createdAt**: The date and time when the task was created {Fecha y hora de creación}.
- **updatedAt**: The date and time when the task was last updated {Fecha y hora de última actualización}.
## Example Commands

```bash
# Adding a new task
task-cli add "Buy groceries"
# Output: Task added successfully (ID: 1)

# Updating and deleting tasks
task-cli update 1 "Buy groceries and cook dinner"
task-cli delete 1

# Marking a task as in progress or done
task-cli mark-in-progress 1
task-cli mark-done 1

# Listing all tasks
task-cli list

# Listing tasks by status
task-cli list done
task-cli list todo
task-cli list in-progress
```
# Task Properties {Propiedades de la Tarea}

Each task should have the following properties:
{Cada tarea debe tener las siguientes propiedades:}

- **id**: A unique identifier for the task {Un identificador único para la tarea}.
- **description**: A short description of the task {Una descripción corta de la tarea}.
- **status**: The status of the task (**todo**, **in-progress**, **done**) {El estado de la tarea}.
- **createdAt**: The date and time when the task was created {La fecha y hora en que la tarea fue creada}.
- **updatedAt**: The date and time when the task was last updated {La fecha y hora en que la tarea fue actualizada por última vez}.

Make sure to add these properties to the JSON file when adding a new task and update them when updating a task.
{Asegúrate de agregar estas propiedades al archivo JSON al agregar una nueva tarea y actualizarlas al modificar una tarea.}

# Getting Started {Empezando}

## Set Up Your Development Environment {Configura tu entorno de desarrollo}

- Choose a programming language you are comfortable with (e.g., Python, JavaScript, etc.).
- Ensure you have a code editor or IDE installed (e.g., VSCode, PyCharm).

## Project Initialization {Inicialización del proyecto}

- Create a new project directory for your Task Tracker CLI.
- Initialize a version control system (e.g., Git) to manage your project.

## Implementing Features {Implementación de funcionalidades}

- Start by creating a basic CLI structure to handle user inputs.
- Implement each feature one by one, ensuring to test thoroughly before moving to the next:
  {Implementa cada funcionalidad una por una, asegurando probar a fondo antes de pasar a la siguiente:}
  1. Implement **adding** {agregar} task functionality first.
  2. **Listing** {listar} tasks next.
  3. Then **updating** {actualizar}, **marking as in progress** {marcar como en progreso}, etc.

## Testing and Debugging {Pruebas y Depuración}

- Test each feature individually to ensure they work as expected.
- Verify the JSON file to ensure tasks are being stored correctly.
- Debug any issues that arise during development.

## Finalizing the Project {Finalización del proyecto}

- Ensure all features are implemented and tested.
- Clean up your code and add comments where necessary.
- Write a good **README** file on how to use your Task Tracker CLI.

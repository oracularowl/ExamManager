import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import random

class Question:
    def __init__(self, question_text, options, correct_option):
        self.question_text = question_text
        self.options = options
        self.correct_option = correct_option

    def check_answer(self, user_answer):
        return self.correct_option == user_answer

class Exam:
    def __init__(self, root):
        self.root = root
        self.questions = None
        self.score = 0
        self.current_question = 0
        self.user_answers = []

        self.create_start_screen()

    def create_start_screen(self):
        self.start_frame = tk.Frame(self.root)
        self.start_frame.pack(padx=20, pady=20)

        tk.Label(self.start_frame, text="Welcome to OracularOwl's Exam Manager", font=("Arial", 18)).pack(pady=10)

        try:
            img = Image.open("welcome_image.png")
            img = img.resize((400, 300), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(self.start_frame, image=self.photo).pack(pady=10)
        except Exception as e:
            print("Error loading image:", e)

        tk.Button(self.start_frame, text="Select Question File", font=("Arial", 14), 
                 command=self.select_file).pack(pady=5)
        
        self.start_button = tk.Button(self.start_frame, text="Start Exam", font=("Arial", 14), 
                                    command=self.start_exam, state="disabled")
        self.start_button.pack(pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Exam Questions File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.questions = load_questions_from_file(file_path)
            if self.questions:
                random.shuffle(self.questions)
                self.start_button.config(state="normal")
                messagebox.showinfo("Success", f"Loaded {len(self.questions)} questions successfully!")
            else:
                messagebox.showerror("Error", "No valid questions found in the selected file.")
                self.questions = None
                self.start_button.config(state="disabled")

    def start_exam(self):
        if not self.questions:
            messagebox.showwarning("Warning", "Please select a question file first!")
            return
        self.start_frame.destroy()
        self.create_exam_ui()

    def create_exam_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.question_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 14),
            anchor="w",
            justify="left",
            wraplength=600
        )
        self.question_label.grid(row=0, column=0, padx=10, pady=5)

        self.option_var = tk.IntVar()

        self.option_buttons = []
        for i in range(4):
            option_button = tk.Radiobutton(self.frame, text="", variable=self.option_var, value=i+1, font=("Arial", 12))
            option_button.grid(row=i+1, column=0, sticky="w", padx=10, pady=5)
            self.option_buttons.append(option_button)

        self.submit_button = tk.Button(self.frame, text="Submit", command=self.submit_answer, font=("Arial", 12))
        self.submit_button.grid(row=5, column=0, pady=10)

        self.next_button = tk.Button(self.frame, text="Next", command=self.next_question, font=("Arial", 12))
        self.next_button.grid(row=5, column=1, pady=10, padx=10)
        self.next_button.grid_remove()

        self.end_button = tk.Button(self.frame, text="End Exam", command=self.end_exam, font=("Arial", 12))
        self.end_button.grid(row=5, column=2, pady=10, padx=10)

        self.feedback_label = tk.Label(self.frame, text="", font=("Arial", 12), fg="green")
        self.feedback_label.grid(row=6, column=0, padx=10, pady=5, columnspan=3)

        self.completion_label = tk.Label(self.frame, text="", font=("Arial", 18), fg="blue", justify="center")
        self.completion_label.grid(row=7, column=0, padx=10, pady=20, columnspan=3)

        self.review_button = None

        self.update_question()

    def update_question(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            numbered_text = f"Question {self.current_question + 1}/{len(self.questions)}: {question.question_text}"
            
            for option_button in self.option_buttons:
                option_button.config(fg="black", state="normal")
            
            self.submit_button.grid()
            self.next_button.grid_remove()
            self.feedback_label.config(text="")
            self.submit_button.config(state="normal")
            self.end_button.config(state="normal")

            self.question_label.config(text=numbered_text)
            for i in range(4):
                self.option_buttons[i].config(text=question.options[i])

            if self.current_question < len(self.user_answers):
                self.option_var.set(self.user_answers[self.current_question])
            else:
                self.option_var.set(0)
        else:
            self.end_exam()

    def submit_answer(self):
        user_answer = self.option_var.get()
        if user_answer == 0:
            messagebox.showwarning("Warning", "Please select an answer.")
            return

        question = self.questions[self.current_question]

        if self.current_question < len(self.user_answers):
            self.user_answers[self.current_question] = user_answer
        else:
            self.user_answers.append(user_answer)

        for button in self.option_buttons:
            button.config(state="disabled")
        self.submit_button.config(state="disabled")

        if question.check_answer(user_answer):
            self.score += 1
            self.feedback_label.config(text="Correct!", fg="green")
            self.root.after(1000, self.next_question)
        else:
            self.feedback_label.config(
                text="Incorrect! Correct answer: " + question.options[question.correct_option - 1],
                fg="red"
            )
            self.highlight_correct_answer(question)
            self.next_button.grid()

    def next_question(self):
        self.current_question += 1
        self.update_question()

    def highlight_correct_answer(self, question):
        correct_answer_index = question.correct_option - 1
        self.option_buttons[correct_answer_index].config(fg="green")

    def end_exam(self):
        for widget in self.frame.winfo_children():
            widget.grid_forget()

        score_percentage = (self.score / len(self.questions)) * 100 if self.questions else 0
        completeness_message = (
            f"Congratulations! You have completed the exam.\n"
            f"Your score: {self.score}/{len(self.questions)} ({score_percentage:.2f}%)"
        )

        self.completion_label.config(text=completeness_message)
        self.completion_label.grid(row=0, column=0, padx=10, pady=20)

        self.review_button = tk.Button(self.frame, text="Review Answers", command=self.review_answers, font=("Arial", 12))
        self.review_button.grid(row=1, column=0, pady=10)

        # Add Start New Exam button
        self.new_exam_button = tk.Button(self.frame, text="Start New Exam", command=self.start_new_exam, font=("Arial", 12))
        self.new_exam_button.grid(row=1, column=1, pady=10, padx=10)

    def start_new_exam(self):
        # Reset all exam variables
        self.score = 0
        self.current_question = 0
        self.user_answers = []
        self.questions = None
        
        # Destroy current frame and return to start screen
        self.frame.destroy()
        self.create_start_screen()

    def review_answers(self):
        review_window = tk.Toplevel(self.root)
        review_window.title("Review Answers")
        review_frame = tk.Frame(review_window)
        review_frame.pack(padx=10, pady=10)

        for i, question in enumerate(self.questions):
            answer_result = "Correct" if question.check_answer(self.user_answers[i]) else "Incorrect"
            result_color = "green" if answer_result == "Correct" else "red"

            tk.Label(review_frame, text=f"Q{i+1}: {question.question_text}", font=("Arial", 12), anchor="w", wraplength=600, justify="left").pack(anchor="w", padx=5, pady=5)
            tk.Label(review_frame, text=f"Your Answer: {question.options[self.user_answers[i] - 1]}", font=("Arial", 12), anchor="w").pack(anchor="w", padx=5)
            tk.Label(review_frame, text=f"Result: {answer_result}", font=("Arial", 12), fg=result_color, anchor="w").pack(anchor="w", padx=5, pady=10)

def load_questions_from_file(filename):
    questions = []
    try:
        with open(filename, 'r') as file:
            while True:
                question_text = file.readline().strip()
                if not question_text:
                    break

                options_line = file.readline().strip()
                if not options_line:
                    break
                options = options_line.split('|')

                if len(options) != 4:
                    continue

                try:
                    correct_option = int(file.readline().strip())
                except ValueError:
                    continue

                if correct_option < 1 or correct_option > 4:
                    continue

                question = Question(question_text, options, correct_option)
                questions.append(question)
    except FileNotFoundError:
        messagebox.showerror("Error", f"The file '{filename}' was not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Error loading file: {str(e)}")
    return questions

if __name__ == "__main__":
    root = tk.Tk()
    root.title("OracularOwl's Exam Manager")
    root.geometry("1024x768")
    
    exam = Exam(root)
    root.mainloop()

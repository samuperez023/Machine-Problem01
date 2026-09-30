# Machine-Problem01

Expense Tracker & Budget Manager (CLI & Functional Edition)


Overview
The project will be completed as a group activity, where the group will develop an Expense Tracker & Budget Manager — a Management Information System designed to help users record, categorize, and analyze daily expenses. The system will follow structured procedural and modular programming principles, organizing business logic, data operations, and user workflows into distinct sets of reusable functions. The system will feature an interactive Command-Line Interface (CLI) menu for user interaction, coordinated through a standard main() entry-point function.

The project will implement at least four (4) core functional modules/groups, each responsible for a distinct set of operations:
Transaction Operations Functions: Creating, formatting, and validating individual expense entries.
Budget & Analytics Functions: Calculating totals, filtering records, and computing category-wise summaries.
File Handling & Storage Functions: Saving, loading, and parsing records using persistent local storage (CSV or JSON).
CLI & Menu Navigation Functions: Presenting interactive console menus, reading and validating user inputs, and printing formatted tabular reports.
The program execution must be orchestrated through a central main() function protected by the standard execution boilerplate (if __name__ == "__main__": main()). Data will be passed between functions using standard data structures (e.g., lists of dictionaries or structured records) to produce the required outputs.



Objectives
Develop an interactive, robust, and user-friendly menu-driven CLI for recording and managing expenses.
Apply modular programming concepts (functional decomposition, parameter passing, return values, separation of concerns).
Implement a dedicated main() function to oversee program initialization, menu loop routing, state management, and termination.
Provide real-time computation of total expenses and breakdown by category using dedicated calculation functions.
Implement dedicated file I/O functions to save and load transactions across sessions (CSV or JSON).
Enable users to view, search, and analyze their spending habits through cleanly formatted terminal reports.


Programming Logic Structures
The project will implement standard programming structures within procedural function flows:

Sequence: Step-by-step execution within functions (e.g., main() initializes storage → displays menu → prompts input → validates data → updates records → saves to disk).
Selection (Decision-Making): Conditional structures (if-elif-else, match-case) for:
Input validation (checking that amounts are positive numeric values, dates are valid, etc.).
Routing menu choices within main() to their respective handling functions.
Verifying if a category exists before calculating a summary.
Handling missing data, invalid menu options, or unreadable files.
Iteration (Loops):
An event/control loop inside main() (while True) to keep the CLI menu running until the user selects "Exit".
for loops to iterate over transaction collections to compute sums, filter by dates, or format tabular rows for console display.
File reading/writing loops to parse or serialize records line-by-line.


Program Structure & Key Functional Areas
0. Program Driver (main() Function)
The central orchestrator of the entire application:

main() Function:
Loads saved transactions on startup by invoking the storage module.
Runs the primary interactive application loop.
Receives user menu selections and routes execution to corresponding feature functions.
Handles program exit and ensures records are safely saved before termination.
Executed cleanly via:
                     if __name__ == "__main__":

                             main()

1. Transaction Operations Functions
Dedicated to creating, sanitizing, and validating individual transaction records:

create_transaction(date, category, amount, description): Constructs a structured transaction record (e.g., a dictionary).
validate_transaction_data(date, category, amount): Validates input formats and ensures amounts are positive.
format_transaction(transaction): Returns a cleanly formatted string representation of a single entry.
2. Budget & Analytics Functions
Contains the core business and calculation logic:

calculate_total_expenses(transactions): Computes the aggregate sum of all logged expenses.
get_category_summary(transactions): Aggregates total spending grouped by unique categories.
filter_transactions(transactions, filter_by, criteria): Returns a filtered list of records based on category, date range, or keyword.
3. File Handling & Storage Functions
Handles all persistent storage operations independently from the user interface:

save_transactions_to_file(transactions, filename): Writes current records to a local CSV or JSON file.
load_transactions_from_file(filename): Reads stored records from disk, gracefully handling missing or empty files.
parse_file_data(raw_data): Sanitizes and transforms raw file rows into internal program data structures.
4. Console Interface & Menu Navigation Functions
Controls terminal display, user prompts, and program formatting:

display_main_menu(): Renders the numbered options available to the user.
prompt_user_input(prompt_text, expected_type): Safely accepts and parses user responses.
display_transactions_table(transactions): Prints an aligned, formatted ASCII table of expense records.
(Optional Visual Feature: A dedicated function like plot_expense_summary(summary_data) can use libraries like Matplotlib to display spending charts).



Expected Output
A fully functional terminal/console application where users can:

Launch the program seamlessly through a structured main() function.
Navigate an interactive, menu-driven CLI.
Record, edit, and categorize daily expenses via validated inputs.
Automatically view real-time spending totals and category breakdowns.
Save and load all expense records persistently across sessions.
View structured, aligned tabular summaries directly in the terminal window.


Guidelines & Milestones
October 8, 2026 (Class Schedule) – Final submission and presentation
The project should be simple, user-friendly, interactive, and fully functional. Your grade will depend on how effectively the features are presented, the ease of navigation, and the technical soundness of the system.



Grading Criteria
Presentation Quality (20%) – The presentation must be clear, organized, and engaging. Documentation should be well-written and easy to follow. Diagrams or visual aids must be neat and informative. If an oral presentation is required, group members should speak clearly, confidently, and follow a logical structure.
Programming Logic Structures (30%) – The program should clearly demonstrate the use of programming logic structures, functional modularity, and proper implementation of the main() function and helper functions.
Documentation (20%) – The output should be properly documented with clear explanations, functional flowcharts/structure charts, organized layouts, and relevant comments in the code.
Teamwork (30%) – The group should show effective collaboration and task distribution. All members must contribute to the project and take responsibility for their assigned parts. Teams should solve problems together, manage time well, and meet deadlines.


Presentation Details
A recorded presentation is required on or before October 8, 2026, before class schedule. The group will have a duration between 10 to 15 minutes (strictly enforced). Members must wear semi-formal attire.

If a member fails to fulfill their responsibilities, the entire group’s performance will be affected. Teams have the option to remove a member who contributes insignificantly. Non-contributing members must be reported with valid proof to the instructor. Although this is a group project, grading is done individually. Each member should have a specific role in the presentation and demonstrate both communication and critical thinking skills.



Deliverables
Video Presentation: Upload your recorded group presentation (10–15 minutes, semi-formal attire) to YouTube as Unlisted and share the link in your submission.
Presentation File: Submit a PDF copy of your PowerPoint or Canva presentation slides.
Project Documentation & Source Code: Prepare the documentation following the given template, include functional breakdowns and flowcharts, and submit it along with your Python source code files as a PDF/archive.
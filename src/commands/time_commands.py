# src/commands/time_commands.py
from services.time_library import preSet_time_library


def register_time_commands(bolt_app, state):
    @bolt_app.command("/findtime")
    def handle_findtime_command(ack, respond):
        try:
            ack()
            respond(f"Today's random scheduled prompt time is {state.get_daily_target_time()}")
        except Exception as e:
            print(f"Error handling /findtime command: {e}")

    @bolt_app.command("/picktime")
    def pick_time(ack, respond, body):
        try:
            ack()
            text = body.get("text", "").strip()

            if not text:
                respond(
                    "Available time options:\n"
                    "1. 12:00:00 PM\n"
                    "2. 12:30:00 PM\n"
                    "3. 01:00:00 PM\n"
                    "4. 01:30:00 PM\n"
                    "5. 02:00:00 PM\n"
                    "6. 02:30:00 PM\n"
                    "7. 03:00:00 PM\n"
                    "8. 03:30:00 PM\n"
                    "9. 04:00:00 PM\n"
                    "10. 04:30:00 PM\n"
                    "11. 05:00:00 PM\n\n"
                    "Use `/picktime <number>` to set a specific time (e.g., `/picktime 5` for 02:00:00 PM)"
                )
                return

            try:
                choice = int(text)
            except ValueError:
                respond("Please provide a valid number between 1 and 11 to set the time")
                return

            if 1 <= choice <= 11:
                daily_target_time = preSet_time_library(choice)
                state.set_daily_target_time(daily_target_time)
                respond(f"Time set to: {daily_target_time}")
                print(f"Daily target time set to: {daily_target_time}")
            else:
                respond("Must pick a number between 1 and 11 to set the time.")

        except Exception as e:
            print(f"Error handling /picktime command: {e}")
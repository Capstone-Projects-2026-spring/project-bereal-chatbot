---
sidebar_position: 4
---
# Test Report

---

## Unit Test Output

Tests covering isolated components: time library, config validation, and command handlers.

```
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[1-09:30:00 AM] PASSED                                                                                  [ 70%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[2-09:35:00 AM] PASSED                                                                                  [ 72%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[3-09:40:00 AM] PASSED                                                                                  [ 73%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[4-09:45:00 AM] PASSED                                                                                  [ 75%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[5-09:50:00 AM] PASSED                                                                                  [ 76%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[6-09:55:00 AM] PASSED                                                                                  [ 77%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[7-10:00:00 AM] PASSED                                                                                  [ 79%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[8-10:05:00 AM] PASSED                                                                                  [ 80%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[9-10:10:00 AM] PASSED                                                                                  [ 82%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[10-10:15:00 AM] PASSED                                                                                 [ 83%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[11-10:20:00 AM] PASSED                                                                                 [ 85%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[12-10:25:00 AM] PASSED                                                                                 [ 86%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[13-10:30:00 AM] PASSED                                                                                 [ 88%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[14-10:35:00 AM] PASSED                                                                                 [ 89%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[15-10:40:00 AM] PASSED                                                                                 [ 91%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[16-10:45:00 AM] PASSED                                                                                 [ 92%]
tests/test_timeLibrary.py::test_preset_time_library_valid_choices[17-10:50:00 AM] PASSED                                                                                 [ 94%]
tests/test_timeLibrary.py::test_preset_time_library_invalid_choices_return_none[0] PASSED                                                                                [ 95%]
tests/test_timeLibrary.py::test_preset_time_library_invalid_choices_return_none[18] PASSED                                                                               [ 97%]
tests/test_timeLibrary.py::test_preset_time_library_invalid_choices_return_none[-1] PASSED                                                                               [ 98%]
tests/test_timeLibrary.py::test_preset_time_library_invalid_choices_return_none[999] PASSED                                                                              [100%]
tests/test_config.py::test_required_env_var_is_set[SLACK_BOT_TOKEN] PASSED                                                                                               [ 45%]
tests/test_config.py::test_required_env_var_is_set[SLACK_APP_TOKEN] PASSED                                                                                               [ 47%]
tests/test_config.py::test_required_env_var_is_set[SLACK_SIGNING_SECRET] PASSED                                                                                          [ 48%]
tests/test_config.py::test_required_env_var_is_set[SLACK_CLIENT_ID] PASSED                                                                                               [ 50%]
tests/test_config.py::test_required_env_var_is_set[SLACK_CLIENT_SECRET] PASSED                                                                                           [ 51%]
tests/test_config.py::test_required_env_var_is_set[SLACK_REDIRECT_URI] PASSED                                                                                            [ 52%]
tests/test_config.py::test_required_env_var_is_set[MONGO_URI] PASSED                                                                                                     [ 54%]
tests/test_config.py::test_slack_bot_token_format PASSED                                                                                                                 [ 55%]
tests/test_config.py::test_slack_app_token_format PASSED                                                                                                                 [ 57%]
tests/test_commands.py::test_forceprompt_acks PASSED                                                                                                                     [  7%]
tests/test_commands.py::test_forceprompt_posts_to_command_channel PASSED                                                                                                 [  8%]
tests/test_commands.py::test_forceprompt_posts_to_specified_channel PASSED                                                                                               [ 10%]
tests/test_commands.py::test_setchannel_updates_state PASSED                                                                                                             [ 11%]
tests/test_commands.py::test_setchannel_rejects_missing_channel PASSED                                                                                                   [ 13%]
tests/test_commands.py::test_picktags_command_opens_static_checkbox_modal PASSED                                                                                         [ 14%]
tests/test_commands.py::test_picktags_submission_saves_selected_tags PASSED                                                                                              [ 16%]
tests/test_commands.py::test_social_connector_finds_pair_from_shared_tags PASSED                                                                                         [ 17%]
tests/test_commands.py::test_social_connector_randomly_selects_from_all_matching_pairs PASSED                                                                            [ 19%]
tests/test_commands.py::test_social_connector_posts_soft_intro_message PASSED                                                                                            [ 20%]
tests/test_commands.py::test_social_connector_command_posts_in_current_channel PASSED                                                                                    [ 22%]
tests/test_commands.py::test_social_connector_command_responds_when_no_match_found PASSED                                                                                [ 23%]
tests/test_commands.py::test_promptstats_returns_sorted_summary PASSED                                                                                                   [ 25%]
tests/test_commands.py::test_promptstats_handles_empty_data PASSED                                                                                                       [ 26%]
tests/test_commands.py::test_picktopic_lists_topics_when_no_arg PASSED                                                                                                   [ 27%]
tests/test_commands.py::test_picktopic_sets_pending_topic_when_valid PASSED                                                                                              [ 29%]
tests/test_commands.py::test_picktopic_rejects_unknown_topic PASSED                                                                                                      [ 30%]
tests/test_commands.py::test_findtime_returns_target_time_and_mode PASSED                                                                                                [ 32%]
tests/test_commands.py::test_picktime_lists_options_when_empty PASSED                                                                                                    [ 33%]
tests/test_commands.py::test_picktime_sets_target_time_for_valid_choice PASSED                                                                                           [ 35%]
tests/test_commands.py::test_picktime_rejects_invalid_input PASSED                                                                                                       [ 36%]
tests/test_commands.py::test_vibestatus_random_mode_summary PASSED                                                                                                       [ 38%]
tests/test_commands.py::test_vibestatus_static_mode_summary PASSED                                                                                                       [ 39%]
tests/test_commands.py::test_help_returns_setup_guide_text PASSED                                                                                                        [ 41%]
tests/test_commands.py::test_streak_personal_no_streak PASSED                                                                                                            [ 42%]
tests/test_commands.py::test_streak_leaderboard_responds PASSED                                                                                                          [ 44%]

============================================================================= 55 passed =============================================================================
```

---

## Integration Test Output

Tests covering state management and cross-component behavior.

```
tests/test_integration.py::test_state_default_channel PASSED                                                                                                             [ 58%]
tests/test_integration.py::test_state_set_and_get_active_channel PASSED                                                                                                  [ 60%]
tests/test_integration.py::test_state_set_and_get_mode PASSED                                                                                                            [ 61%]
tests/test_integration.py::test_state_set_and_get_static_time PASSED                                                                                                     [ 63%]
tests/test_integration.py::test_state_active_days_default_all_days PASSED                                                                                                [ 64%]
tests/test_integration.py::test_state_set_active_days PASSED                                                                                                             [ 66%]
tests/test_integration.py::test_state_is_today_active PASSED                                                                                                             [ 67%]
tests/test_integration.py::test_state_is_today_inactive_when_days_cleared PASSED                                                                                         [ 69%]

============================================================================= 8 passed =============================================================================
```

---

## Automated Acceptance Test Output

Tests verifying end-to-end scheduler and state flow behavior.

```
tests/test_acceptance.py::test_pick_random_time_from_range PASSED                                                                                                        [  1%]
tests/test_acceptance.py::test_pick_random_time_falls_back_to_preset_when_no_range PASSED                                                                                [  2%]
tests/test_acceptance.py::test_pick_random_time_after_filters_past_times PASSED                                                                                          [  4%]
tests/test_acceptance.py::test_full_flow_state_and_scheduler PASSED                                                                                                      [  5%]

============================================================================= 4 passed =============================================================================
```

---

## Manual Acceptance Test Procedures

Each procedure was performed manually and observed results are noted below.

| # | Procedure | Performed | Observed Result |
|---|-----------|-----------|-----------------|
| 1 | Install VibeCheck into a Slack workspace via OAuth flow | Yes | Bot successfully installed to Slack server |
| 2 | Run /setchannel #channel-name and verify the active channel updates | Yes | Bot responds and channel is set |
| 3 | Run /forceprompt and verify prompt is posted to the command channel | Yes | Prompt posted to correct channel immediately |
| 4 | Run /forceprompt #other-channel and verify override channel is used | Yes | Prompt posted to the specified channel |
| 5 | Run /picktags and verify checkbox modal opens with available tags | Yes | Modal opened with correct checkboxes and pre-selected existing tags |
| 6 | Submit tag selection and verify DM confirmation is sent | Yes | Tags saved; confirmation DM received |
| 7 | Run /connect and verify a matched user pair is announced | Yes | Pair announced |
| 8 | Run /connect with no eligible pair and verify no-match response | Yes | No-match message returned, no announcement |
| 9 | Run /findtime and verify target time and mode are reported | Yes | Correct time and mode returned |
| 10 | Run /picktime with no argument and verify preset list is shown | Yes | Preset list displayed with usage instructions |
| 11 | Run /picktime 3 and verify state updates to selected time | Yes | State updated; confirmation time returned |
| 12 | Run /vibestatus and verify channel, mode, time, and active days shown | Yes | All workspace status fields present in response |
| 13 | Run /promptstats and verify sorted prompt engagement summary | Yes | Summary returned with response counts, returns engagement |
| 14 | Run /picktopic with no argument and verify topic list shown | Yes | Topic list is displayed |
| 15 | Run `/picktopic [topic]` and verify pending topic is stored | Yes | Topic is picked |
| 16 | Run /help and verify setup guide text is returned | Yes | A list of commands to guide users is returned |
| 17 | Run /streak and verify personal streak or leaderboard responds | Yes | Streak summary returned |

---

## List of Known Problems

No test failures were observed. All 68 automated tests passed.

| Test | Status | Description |
|------|--------|-------------|
| — | — | No known failures at time of this report |

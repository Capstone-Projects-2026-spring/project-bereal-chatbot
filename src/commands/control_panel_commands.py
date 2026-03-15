@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                {
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Time Configuration Settings"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*1. Select Operation Mode*"
			},
			"accessory": {
				"type": "radio_buttons",
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Random Time"
						},
						"value": "mode_random"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Preset Time Select"
						},
						"value": "mode_preset"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Static Set Time"
						},
						"value": "mode_static"
					}
				],
				"action_id": "mode_selection"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*2. Random Time Range Parameters:*"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "start_time",
				"placeholder": {
					"type": "plain_text",
					"text": "Start (HH:MM:SS)"
				}
			},
			"label": {
				"type": "plain_text",
				"text": "Start Time"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "end_time",
				"placeholder": {
					"type": "plain_text",
					"text": "End (HH:MM:SS)"
				}
			},
			"label": {
				"type": "plain_text",
				"text": "End Time"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*3. Preset Times Select:*"
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "radio_buttons",
					"initial_option": {
						"text": {
							"type": "plain_text",
							"text": "12:00:00 PM"
						},
						"value": "time_1"
					},
					"options": [
						{
							"text": {
								"type": "plain_text",
								"text": "12:00:00 PM"
							},
							"value": "time_1"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "12:30:00 PM"
							},
							"value": "time_2"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "01:00:00 PM"
							},
							"value": "time_3"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "01:30:00 PM"
							},
							"value": "time_4"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "02:00:00 PM"
							},
							"value": "time_5"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "02:30:00 PM"
							},
							"value": "time_6"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "03:00:00 PM"
							},
							"value": "time_7"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "03:30:00 PM"
							},
							"value": "time_8"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "04:00:00 PM"
							},
							"value": "time_9"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "04:30:00 PM"
							},
							"value": "time_10"
						}
					],
					"action_id": "preset_time_selection"
				}
			]
		},
		{
			"type": "divider"
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "static_entry",
				"placeholder": {
					"type": "plain_text",
					"text": "E.g. 09:15:00 AM"
				}
			},
			"label": {
				"type": "plain_text",
				"text": "*4. Static Set Time (Manual)*"
			}
		}
	]
}
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
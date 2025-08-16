import random

import gradio
import gradio as gr
import main
import API.Oogabooga_Api_Support
import utils.logging
import utils.settings
import utils.hotkeys
import utils.tag_task_controller
import utils.voice
import utils.i18n
import json

# Inizializza sistema i18n
from utils.i18n import _

# Import the gradio theme color
with open("Configurables/GradioThemeColor.json", 'r') as openfile:
    gradio_theme_color = json.load(openfile)

based_theme = gr.themes.Base(
    primary_hue=gradio_theme_color,
    secondary_hue="indigo",
    neutral_hue="zinc",

)



with gr.Blocks(theme=based_theme, title=_("app_title")) as demo:

    #
    # CHAT
    #

    with gr.Tab(_("tabs.chat")):

        #
        # Main Chatbox
        #

        chatbot = gr.Chatbot(height=540)

        with gr.Row():
            msg = gr.Textbox(scale=3)

            def respond(message, chat_history):

                # No send blank: use button for that!
                if message == "":
                    return ""

                main.main_web_ui_chat(message)

                # Retrieve the result now
                # message_reply = API.Oogabooga_Api_Support.receive_via_oogabooga()
                #
                # chat_history.append((message, message_reply))

                return ""   # Note: Removed the update to the chatbot here, as it is done anyway in the update_chat()!

            def update_chat():
                # Return whole chat, plus the one I have just sent
                if API.Oogabooga_Api_Support.currently_sending_message != "":

                    # Prep for viewing without metadata
                    chat_combine = API.Oogabooga_Api_Support.ooga_history[-30:]
                    i = 0
                    while i < len(chat_combine):
                        chat_combine[i] = chat_combine[i][:2]
                        i += 1
                    chat_combine.append([API.Oogabooga_Api_Support.currently_sending_message, API.Oogabooga_Api_Support.currently_streaming_message])

                    return chat_combine[-30:]


                # Return whole chat, last 30
                else:
                    chat_combine = API.Oogabooga_Api_Support.ooga_history[-30:]
                    i = 0
                    while i < len(chat_combine):
                        chat_combine[i] = chat_combine[i][:2]
                        i += 1

                    return chat_combine


            msg.submit(respond, [msg, chatbot], [msg])

            send_button = gr.Button(variant="primary", value=_("buttons.send"))
            send_button.click(respond, inputs=[msg, chatbot], outputs=[msg])

        demo.load(update_chat, every=0.05, outputs=[chatbot])

        #
        # Basic Mic Chat
        #

        def recording_button_click():

            utils.hotkeys.speak_input_toggle_from_ui()

            return


        with gradio.Row():

            recording_button = gr.Button(value=_("buttons.mic_toggle"))
            recording_button.click(fn=recording_button_click)

            recording_checkbox_view = gr.Checkbox(label=_("status.now_recording"))




        #
        # Buttons
        #

        with gradio.Row():

            def regenerate():
                main.main_web_ui_next()
                return

            def send_blank():
                # Give us some feedback
                print("\nSending blank message...\n")

                # Send the blank
                main.main_web_ui_chat("")
                return

            def undo():
                main.main_undo()
                return

            button_regen = gr.Button(value=_("buttons.reroll"))
            button_blank = gr.Button(value=_("buttons.send_blank"))
            button_undo = gr.Button(value=_("buttons.undo"))

            button_regen.click(fn=regenerate)
            button_blank.click(fn=send_blank)
            button_undo.click(fn=undo)


        #
        # Autochat Settings
        #

        def autochat_button_click():

            utils.hotkeys.input_toggle_autochat_from_ui()

            return


        def change_autochat_sensitivity(autochat_sens):

            utils.hotkeys.input_change_listener_sensitivity_from_ui(autochat_sens)
            return


        with gradio.Row():

            autochat_button = gr.Button(value=_("buttons.toggle_auto_chat"))
            autochat_button.click(fn=autochat_button_click)

            autochat_checkbox_view = gr.Checkbox(label=_("status.auto_chat_enabled"))

            autochat_sensitivity_slider = gr.Slider(minimum=4, maximum=144, value=20, label=_("sliders.auto_chat_sensitivity"))
            autochat_sensitivity_slider.change(fn=change_autochat_sensitivity, inputs=autochat_sensitivity_slider)


        #
        # Semi-Auto Chat Settings
        #

        def semi_auto_chat_button_click():

            # Toggle
            utils.settings.semi_auto_chat = not utils.settings.semi_auto_chat

            # Disable
            utils.hotkeys.disable_autochat()

            return


        with gradio.Row():
            semi_auto_chat_button = gr.Button(value=_("buttons.toggle_semi_auto_chat"))
            semi_auto_chat_button.click(fn=semi_auto_chat_button_click)

            semi_auto_chat_checkbox_view = gr.Checkbox(label=_("status.semi_auto_chat_enabled"))


        def update_settings_view():
            return utils.hotkeys.get_speak_input(), utils.hotkeys.get_autochat_toggle(), utils.settings.semi_auto_chat


        demo.load(update_settings_view, every=0.05,
                  outputs=[recording_checkbox_view, autochat_checkbox_view, semi_auto_chat_checkbox_view])




    #
    # VISUAL
    #

    if utils.settings.vision_enabled:
        with gr.Tab(_("tabs.visual")):

            #
            # Take / Retake Image
            #

            with gr.Row():
                def take_image_button_click():
                    utils.hotkeys.view_image_from_ui()

                    return

                take_image_button = gr.Button(value=_("buttons.take_send_image"))
                take_image_button.click(fn=take_image_button_click)


            #
            # Image Feed
            #

            with gr.Row():
                def cam_use_image_feed_button_click():
                    utils.settings.cam_use_image_feed = not utils.settings.cam_use_image_feed

                    return


                with gr.Row():
                    cam_use_image_feed_button = gr.Button(value=_("buttons.check_uncheck"))
                    cam_use_image_feed_button.click(fn=cam_use_image_feed_button_click)

                    cam_use_image_feed_checkbox_view = gr.Checkbox(label=_("checkboxes.use_image_feed"))


            #
            # Direct Talk
            #

            with gr.Row():
                def cam_direct_talk_button_click():
                    utils.settings.cam_direct_talk = not utils.settings.cam_direct_talk

                    return


                with gr.Row():
                    cam_direct_talk_button = gr.Button(value=_("buttons.check_uncheck"))
                    cam_direct_talk_button.click(fn=cam_direct_talk_button_click)

                    cam_direct_talk_checkbox_view = gr.Checkbox(label=_("checkboxes.direct_talk"))


            #
            # Reply After
            #

            with gr.Row():
                def cam_reply_after_button_click():
                    utils.settings.cam_reply_after = not utils.settings.cam_reply_after

                    return


                with gr.Row():
                    cam_reply_after_button = gr.Button(value=_("buttons.check_uncheck"))
                    cam_reply_after_button.click(fn=cam_reply_after_button_click)

                    cam_reply_after_checkbox_view = gr.Checkbox(label=_("checkboxes.post_reply"))



            #
            # Image Preview
            #

            with gr.Row():
                def cam_image_preview_button_click():
                    utils.settings.cam_image_preview = not utils.settings.cam_image_preview

                    return


                with gr.Row():
                    cam_image_preview_button = gr.Button(value=_("buttons.check_uncheck"))
                    cam_image_preview_button.click(fn=cam_image_preview_button_click)

                    cam_image_preview_checkbox_view = gr.Checkbox(label=_("checkboxes.preview_before_sending"))

            #
            # Capture screenshot
            #

            with gr.Row():
                def cam_capture_screenshot_button_click():
                    utils.settings.cam_use_screenshot = not utils.settings.cam_use_screenshot

                    return


                with gr.Row():
                    cam_capture_screenshot_button = gr.Button(value=_("buttons.check_uncheck"))
                    cam_capture_screenshot_button.click(fn=cam_capture_screenshot_button_click)

                    cam_capture_screenshot_checkbox_view = gr.Checkbox(label=_("checkboxes.capture_screenshot"))

            def update_visual_view():
                return utils.settings.cam_use_image_feed, utils.settings.cam_direct_talk, utils.settings.cam_reply_after, utils.settings.cam_image_preview, utils.settings.cam_use_screenshot


            demo.load(update_visual_view, every=0.05,
                      outputs=[cam_use_image_feed_checkbox_view, cam_direct_talk_checkbox_view, cam_reply_after_checkbox_view, cam_image_preview_checkbox_view, cam_capture_screenshot_checkbox_view])



    #
    # SETTINGS
    #


    with gr.Tab(_("tabs.settings")):

        #
        # Hotkeys
        #

        def hotkey_button_click():
            utils.settings.hotkeys_locked = not utils.settings.hotkeys_locked

            return


        with gr.Row():
            hotkey_button = gr.Button(value=_("buttons.check_uncheck"))
            hotkey_button.click(fn=hotkey_button_click)

            hotkey_checkbox_view = gr.Checkbox(label=_("checkboxes.disable_keyboard_shortcuts"))


        #
        # Shadowchats
        #

        with gr.Row():
            def shadowchats_button_click():
                utils.settings.speak_shadowchats = not utils.settings.speak_shadowchats

                return


            with gr.Row():
                shadowchats_button = gr.Button(value=_("buttons.check_uncheck"))
                shadowchats_button.click(fn=shadowchats_button_click)

                shadowchats_checkbox_view = gr.Checkbox(label=_("checkboxes.speak_typed_chats"))


        #
        # Soft Reset
        #

        with gr.Row():
            def soft_reset_button_click():
                API.Oogabooga_Api_Support.soft_reset()

                return

            soft_reset_button = gr.Button(value=_("buttons.chat_soft_reset"))
            soft_reset_button.click(fn=soft_reset_button_click)


        #
        # Random Memory
        #

        with gr.Row():
            def random_memory_button_click():
                main.main_memory_proc()

                return

            soft_reset_button = gr.Button(value=_("buttons.proc_random_memory"))
            soft_reset_button.click(fn=random_memory_button_click)


        #
        # RP Supression
        #

        with gr.Row():
            def supress_rp_button_click():
                utils.settings.supress_rp = not utils.settings.supress_rp

                return


            with gr.Row():
                supress_rp_button = gr.Button(value=_("buttons.check_uncheck"))
                supress_rp_button.click(fn=supress_rp_button_click)

                supress_rp_checkbox_view = gr.Checkbox(label=_("checkboxes.suppress_rp"))


        #
        # Newline Cut
        #

        with gr.Row():
            def newline_cut_button_click():
                utils.settings.newline_cut = not utils.settings.newline_cut

                return


            with gr.Row():
                newline_cut_button = gr.Button(value=_("buttons.check_uncheck"))
                newline_cut_button.click(fn=newline_cut_button_click)

                newline_cut_checkbox_view = gr.Checkbox(label=_("checkboxes.cutoff_newlines"))


        #
        # Asterisk Ban
        #

        with gr.Row():
            def asterisk_ban_button_click():
                utils.settings.asterisk_ban = not utils.settings.asterisk_ban

                return


            with gr.Row():
                asterisk_ban_button = gr.Button(value=_("buttons.check_uncheck"))
                asterisk_ban_button.click(fn=asterisk_ban_button_click)

                asterisk_ban_checkbox_view = gr.Checkbox(label=_("checkboxes.ban_asterisks"))


        #
        # Token Limit Slider
        #

        with gr.Row():

            def change_max_tokens(tokens_count):

                utils.settings.max_tokens = tokens_count
                return


            token_slider = gr.Slider(minimum=20, maximum=2048, value=utils.settings.max_tokens, label=_("sliders.max_chat_tokens"))
            token_slider.change(fn=change_max_tokens, inputs=token_slider)



        #
        # Alarm Time
        #

        def alarm_button_click(input_time):

            utils.settings.alarm_time = input_time

            print("\nAlarm time set as " + utils.settings.alarm_time + "\n")

            return


        with gr.Row():
            alarm_textbox = gr.Textbox(value=utils.settings.alarm_time, label=_("textboxes.alarm_time"))

            alarm_button = gr.Button(value=_("buttons.change_time"))
            alarm_button.click(fn=alarm_button_click, inputs=alarm_textbox)


        #
        # Language Model Preset
        #

        def model_preset_button_click(input_text):

            utils.settings.model_preset = input_text

            print("\nChanged model preset to " + utils.settings.model_preset + "\n")

            return


        with gr.Row():
            model_preset_textbox = gr.Textbox(value=utils.settings.model_preset, label=_("textboxes.model_preset"))

            model_preset_button = gr.Button(value=_("buttons.change_model_preset"))
            model_preset_button.click(fn=model_preset_button_click, inputs=model_preset_textbox)




        def update_settings_view():

            return utils.settings.hotkeys_locked, utils.settings.speak_shadowchats, utils.settings.supress_rp, utils.settings.newline_cut, utils.settings.asterisk_ban


        demo.load(update_settings_view, every=0.05, outputs=[hotkey_checkbox_view, shadowchats_checkbox_view, supress_rp_checkbox_view, newline_cut_checkbox_view, asterisk_ban_checkbox_view])




    #
    # Tags / Tasks
    #

    with gr.Tab(_("tabs.tags_tasks")):

        #
        # Tasks

        cur_task_box = gr.Textbox(label=_("textboxes.current_task"))

        def update_task_button_click(input_text):

            # Change the task-tag first
            utils.tag_task_controller.change_tag_via_task("Task-" + input_text)

            # Now swap the task
            utils.tag_task_controller.set_task(input_text)



        with gr.Row():
            cur_task_update_box = gr.Textbox(label=_("textboxes.set_new_task"))
            cur_task_update_button = gr.Button(value=_("buttons.update_task"))
            cur_task_update_button.click(fn=update_task_button_click, inputs=cur_task_update_box)

        previous_tasks_box = gr.Textbox(label=_("textboxes.previous_tasks"), lines=7)


        #
        # Gaming Loop

        def update_gaming_loop():
            utils.settings.is_gaming_loop = not utils.settings.is_gaming_loop

        if utils.settings.gaming_enabled:

            with gr.Row():
                gaming_loop_button = gr.Button(value=_("buttons.check_uncheck"))
                gaming_loop_button.click(fn=update_gaming_loop)

                gaming_loop_checkbox_view = gr.Checkbox(label=_("checkboxes.gaming_loop"))


        #
        # Tags

        cur_tags_box = gr.Textbox(label=_("textboxes.current_tags"))

        def update_tags_button_click(new_tags):
            new_tags = new_tags.replace(" ", "")
            new_tags_list = new_tags.split(",")
            print(new_tags_list)

            utils.tag_task_controller.set_tags(new_tags_list)


        with gr.Row():
            cur_tags_update_box = gr.Textbox(label=_("textboxes.set_new_tags"))
            cur_tags_update_button = gr.Button(value=_("buttons.update_tags"))
            cur_tags_update_button.click(fn=update_tags_button_click, inputs=cur_tags_update_box)

        previous_tags_box = gr.Textbox(label=_("textboxes.previous_tags"), lines=7)

        def update_tag_task_view():
            cantonese_task_list = ""
            for task in utils.settings.all_task_char_list:
                cantonese_task_list += task + "\n"

            cantonese_cur_tags_list = ""
            for tag in utils.settings.cur_tags:
                cantonese_cur_tags_list += tag + "\n"

            cantonese_all_tags_list = ""
            for tag in utils.settings.all_tag_list:
                cantonese_all_tags_list += tag + "\n"

            return utils.settings.cur_task_char, cantonese_task_list, cantonese_cur_tags_list, cantonese_all_tags_list

        def update_autogaming_check():
            return utils.settings.is_gaming_loop

        if utils.settings.gaming_enabled:
            demo.load(update_autogaming_check, every=0.05,
                      outputs=[gaming_loop_checkbox_view])

        demo.load(update_tag_task_view, every=0.05, outputs=[cur_task_box, previous_tasks_box, cur_tags_box, previous_tags_box])





    #
    # DEBUG
    #

    with gr.Tab(_("tabs.debug")):
        debug_log = gr.Textbox(utils.logging.debug_log, lines=10, label=_("textboxes.general_debug"), autoscroll=True)
        rag_log = gr.Textbox(utils.logging.rag_log, lines=10, label=_("textboxes.rag_debug"), autoscroll=True)
        kelvin_log = gr.Textbox(utils.logging.kelvin_log, lines=1, label=_("textboxes.temperature_readout"))

        def update_logs():
            return utils.logging.debug_log, utils.logging.rag_log, utils.logging.kelvin_log

        demo.load(update_logs, every=0.05, outputs=[debug_log, rag_log, kelvin_log])



    #
    # LINKS
    #

    with gr.Tab(_("tabs.links")):

        links_text = (
                      _("links.github_project") + ":\n" +
                      "https://github.com/SugarcaneDefender/z-waif \n" +
                      "\n" +
                      _("links.documentation") + ":\n" +
                      "https://docs.google.com/document/d/1qzY09kcwfbZTaoJoQZDAWv282z88jeUCadivLnKDXCo/edit?usp=sharing \n" +
                      "\n" +
                      _("links.youtube") + ":\n" +
                      "https://www.youtube.com/@SugarcaneDefender \n" +
                      "\n" +
                      _("links.support_kofi") + ":\n" +
                      "https://ko-fi.com/zwaif \n" +
                      "\n" +
                      _("links.email_support") + ":\n" +
                      "zwaif77@gmail.com")

        rag_log = gr.Textbox(links_text, lines=14, label=_("textboxes.links"))









def launch_demo():
    demo.launch(server_port=7864)


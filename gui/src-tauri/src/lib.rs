use tauri::menu::{Menu, MenuItem};
use tauri::tray::TrayIconBuilder;

use tauri_plugin_shell::ShellExt;
// use tauri::Listener;

use tauri::WindowEvent;

use enigo::{
    Direction::{Press, Release},
    Enigo, Key, Keyboard, Settings,
};


#[tauri::command]
async fn call_my_sidecar(app: tauri::AppHandle, window: tauri::Window) {
    let sidecar_command = app
    .shell()
    .sidecar("functional_detector")
    .unwrap();


    let _child = sidecar_command.spawn().unwrap().1;

    println!("spawn sidecar");

    window.on_window_event(|e| {
        match e {
            WindowEvent::Destroyed => {
                println!("tryna kill");

                // kill child process
                let mut enigo = Enigo::new(&Settings::default()).unwrap();
                let _ = enigo.key(Key::Escape, Press);
                let _ = enigo.key(Key::Escape, Release);
            },
            _ => ()
        };

        // let mut child = &child;
        // match e {
        //     WindowEvent::Destroyed => {
        //         println!("tryna kill");
        //         child.kill();
        //     },
        //     _ => ()
        // };
    });
}  

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn kill() {
    println!("attempt to kill");
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&quit_i])?;

            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .show_menu_on_left_click(true)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => {
                        // kill child process
                        let mut enigo = Enigo::new(&Settings::default()).unwrap();
                        let _ = enigo.key(Key::Escape, Press);
                        let _ = enigo.key(Key::Escape, Release);

                        println!("quit menu item was clicked");
                        app.exit(0);
                    }
                    _ => {
                        println!("menu item {:?} not handled", event.id);
                    }
                })
                .build(app)?;
            Ok(())
        })
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![call_my_sidecar, kill])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

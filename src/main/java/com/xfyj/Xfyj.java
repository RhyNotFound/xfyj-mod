package com.xfyj;

import com.xfyj.registry.ModItems;
import com.xfyj.registry.ModSounds;

import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.Identifier;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Entrypoint of the 星拂云锦 music disc mod.
 *
 * <p>Registers one custom music disc:
 * <ul>
 *   <li>item: {@code xfyj:music_disc_xfyj} - "S9ryne - 星拂云锦 feat. koi"</li>
 *   <li>sound event: {@code xfyj:music_disc.xfyj}</li>
 *   <li>jukebox song: {@code xfyj:music_disc_xfyj} (data driven, 168 s)</li>
 * </ul>
 */
public class Xfyj implements ModInitializer {
	public static final String MOD_ID = "xfyj";

	// This logger is used to write text to the console and the log file.
	// It is considered best practice to use your mod id as the logger's name.
	// That way, it's clear which mod wrote info, warnings, and errors.
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	@Override
	public void onInitialize() {
		// Sound events first: both the item and the jukebox song data file
		// reference the sound event registered here.
		ModSounds.register();
		ModItems.register();
	}

	public static Identifier id(String path) {
		return Identifier.fromNamespaceAndPath(MOD_ID, path);
	}
}

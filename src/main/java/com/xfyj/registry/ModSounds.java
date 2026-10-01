package com.xfyj.registry;

import com.xfyj.Xfyj;

import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;

/** Registers the sound event that the music disc plays. */
public final class ModSounds {

	/**
	 * Registry path of the sound event.
	 *
	 * <p>Two resources refer to it by name:
	 *
	 * <ul>
	 * <li>{@code data/xfyj/jukebox_song/music_disc_xfyj.json} uses
	 * {@code xfyj:music_disc.xfyj} as the song's sound event;</li>
	 * <li>{@code assets/xfyj/sounds.json} defines that event in terms of the
	 * {@code records/xfyj.ogg} audio file.</li>
	 * </ul>
	 */
	public static final String DISC_SOUND_PATH = "music_disc.xfyj";

	private static SoundEvent discSound;

	private ModSounds() {
	}

	public static void register() {
		Identifier id = Xfyj.id(DISC_SOUND_PATH);

		// createVariableRangeEvent both builds the event and registers it in the
		// sound event registry under this id, which is what the jukebox song
		// resolves against when a record is played.
		discSound = SoundEvent.createVariableRangeEvent(id);

		Xfyj.LOGGER.info("Registered sound event '{}'.", id);
	}

	/** The registered disc sound. */
	public static SoundEvent discSound() {
		return discSound;
	}
}

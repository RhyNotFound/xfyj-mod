package com.xfyj.registry;

import com.xfyj.Xfyj;

import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.JukeboxSong;
import net.minecraft.world.item.Rarity;

/**
 * Registers the "星拂云锦 feat. koi" music disc.
 *
 * <p>The disc is a plain {@link Item} carrying the vanilla jukebox playable
 * component, exactly like vanilla music discs. That component is what lets a
 * jukebox accept the item, spin it and answer with the song's comparator
 * output.
 */
public final class ModItems {

	/** Registry path of both the item and its jukebox song. */
	public static final String DISC_PATH = "music_disc_xfyj";

	/** Registry key of the vanilla "Tools &amp; Utilities" creative tab. */
	private static final ResourceKey<CreativeModeTab> TOOLS_AND_UTILITIES = ResourceKey.create(
			BuiltInRegistries.CREATIVE_MODE_TAB.key(),
			Identifier.fromNamespaceAndPath("minecraft", "tools_and_utilities"));

	private static Item musicDisc;

	private ModItems() {
	}

	public static void register() {
		// The item points at its jukebox song by registry key. Minecraft resolves
		// that key lazily against the loaded data packs, so the entry may be
		// missing at this point in startup without breaking attribution.
		ResourceKey<JukeboxSong> songKey = ResourceKey.create(Registries.JUKEBOX_SONG, Xfyj.id(DISC_PATH));

		Item.Properties properties = new Item.Properties()
				.stacksTo(1)
				.rarity(Rarity.RARE)
				.jukeboxPlayable(songKey);

		ResourceKey<Item> itemKey = ResourceKey.create(BuiltInRegistries.ITEM.key(), Xfyj.id(DISC_PATH));
		musicDisc = Registry.register(BuiltInRegistries.ITEM, itemKey, new Item(properties));

		addToCreativeTab(musicDisc);

		Xfyj.LOGGER.info("Registered music disc '{}'.", itemKey.identifier());
	}

	/** The registered music disc item. */
	public static Item musicDisc() {
		return musicDisc;
	}

	/**
	 * Adds the disc to the vanilla "Tools &amp; Utilities" tab, next to the vanilla
	 * music discs.
	 *
	 * <p>The lambda parameter is left untyped on purpose: {@code
	 * CreativeModeTab.Output} is protected in 26.2 and cannot be named here.
	 */
	private static void addToCreativeTab(Item item) {
		CreativeModeTabEvents.modifyOutputEvent(TOOLS_AND_UTILITIES)
				.register(output -> output.accept(new ItemStack(item)));
	}
}

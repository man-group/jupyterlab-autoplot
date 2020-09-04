// Type definitions for mpld3 v0.3
// Project: mpld3-plugins

export import Axes = require('./Axes');
export import Figure = require('./Figure');
export import Line = require('./Line');
export import Plugin = require('./Plugin');

export as namespace mpld3;

// methods
export function register_plugin(name: string, plugin: Plugin): void;
export function get_element(id: string, fig: Figure): Line;

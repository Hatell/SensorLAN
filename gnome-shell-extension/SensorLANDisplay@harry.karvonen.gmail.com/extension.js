// vi: et sw=2 fileencoding=utf8
//
const Lang = imports.lang;

const Main = imports.ui.main;
const St = imports.gi.St;
const Gio = imports.gi.Gio;

const SensorLANDBusIface = '<node> \
<interface name="org.gnome.Shell.Extensions.SensorLANDisplay"> \
<method name="Display"> \
  <arg type="s" direction="in" name="text"/> \
  <arg type="s" direction="out" name="result"/> \
</method> \
</interface> \
</node>';

let SensorLAN_label = null;
let SensorLAN_bin = null;
let SensorLAN_DBus = null;

const SensorLAN = new Lang.Class({
  Name: "SensorLANDBus",

  _init: function() {
    this._dbusImpl = Gio.DBusExportedObject.wrapJSObject(SensorLANDBusIface, this);
    this._dbusImpl.export( Gio.DBus.session, "/org/gnome/Shell/Extensions/SensorLANDisplay");
  },

  destroy: function() {
    this._dbusImpl.unexport();
  },

  Display: function(text) {
    SensorLAN_label.set_text(text);
    return "OK";
  },
});

function init() {
  if (SensorLAN_label == null) {
    SensorLAN_bin = new St.Bin({ x_fill: false,
                                 x_align:St.Align.MIDDLE });
    SensorLAN_label = new St.Label({text: "No data"});
    SensorLAN_bin.set_child(SensorLAN_label);
  }
}

function enable() {
  if (SensorLAN_DBus == null) {
    SensorLAN_DBus = new SensorLAN();
  }
  Main.panel._centerBox.add_actor(SensorLAN_bin);
}

function disable() {
  if (SensorLAN_DBus) {
    SensorLAN_DBus.destroy();
    SensorLAN_DBus = null;
  }
  Main.panel._centerBox.remove_actor(SensorLAN_bin);
}

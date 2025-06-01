// NOTE: Make sure to reload the browser with cache disabled after making changes to this file.
export default {
  template: `
    <div class="cursor-pointer">
      {{ value }}
      <q-popup-edit v-model="value" auto-save v-slot="scope">
        <q-input v-model="scope.value" dense autofocus counter @keyup.enter="scope.set" />
      </q-popup-edit>
    </div>
`,
  data() {
    console.log("data");
    return {
      value: "Texs",
    };
  },
  methods: {
    handle_click() {
      this.$emit("change", this.value);
    },
    reset() {
      this.value = "jsijij";
    },
  },
  props: {
    title: String,
  },
};

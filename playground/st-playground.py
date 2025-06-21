import himig.constants
import streamlit as st
import himig
import re
import ast

st.title(" 🎵:green[Himig] Playground")
st.write(
    ":green[Python music synthesis module that lets you compose, play, and save melodies.]")

melody = st.session_state.setdefault("melody", [])

cols = st.columns(3)
note = cols[0].selectbox("Note",
                         list(himig.constants.BASE_FREQUENCIES), key="note")
octave = cols[1].selectbox("Octave",
                           range(1, 9), index=3, key="octave")
duration = cols[2].number_input("Duration (s)",
                                min_value=0.1, value=0.5, step=0.1, format="%.1f", key="duration")
if st.button("Add Note"):
    melody.append(f"{note}{octave}:{round(duration, 2)}")

with st.form("notes_form", border=False, enter_to_submit=False):
    with st.expander("Write Your Notes"):
        s = st.text_area(
            "Write valid notes here like: :green-background[C4:0.5,G4:1] or a :green-background[Python list: ['G4:0.5', 'A4:1']]",)
        s_clean = s.strip()
        if s_clean.startswith("[") and s_clean.endswith("]"):
            written_list = ast.literal_eval(s_clean)
        else:
            written_list = s.upper().replace(",", " ").split()

        if st.form_submit_button("Add") and written_list:
            for item in written_list:
                match = re.match(r"([A-G]#?)(\d):([\d.]+)",
                                 item.strip().upper())
                if match:
                    note, octave, duration = match.groups()
                    melody.append(
                        f"{note}{int(octave)}:{round(float(duration), 2)}")

st.subheader("Current Melody")
if melody:
    cols = st.columns([4, 1])
    cols[0].code(melody, wrap_lines=True)
    if cols[1].button("Pop"):
        st.session_state.melody.pop()
        st.rerun()
else:
    st.info(
        "Create your melody by choosing notes and durations or typing them.")


if st.button("Generate", disabled=not st.session_state.melody):
    if all(":" in n and len(n.split(":")) == 2 for n in melody):
        try:
            st.audio(himig.generate_wav_bytes(melody), format="audio/wav")
        except RuntimeError as e:
            st.error(f"Could not generate: {e}")
    else:
        st.warning(
            "Some entries are missing durations or are incorrectly formatted.")

if st.button("Clear Melody", disabled=not st.session_state.melody):
    melody.clear()
    st.rerun()

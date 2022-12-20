python -m codegen_sources.preprocessing.preprocess \
/media/Z/dungnm31/unsafe_safe_rust/mono_data/test \
--langs unsafe safe \
--mode monolingual \
--local True \
--bpe_mode fast \
--fastbpe_vocab_path /media/Z/dungnm31/unsafe_safe_rust/mono_data/safe-unsafe.monolingual.vocab.all \
--fastbpe_code_path /media/Z/dungnm31/unsafe_safe_rust/mono_data/safe-unsafe.monolingual.codes \
--train_splits 1 \
--keep_comments True 
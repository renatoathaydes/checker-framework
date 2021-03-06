/*
 * Copyright (C) 2007 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.common.collect;

import org.checkerframework.checker.nullness.qual.Nullable;
//import javax.annotation.Nullable;
import org.checkerframework.dataflow.qual.Pure;

import java.util.Set;

import com.google.common.annotations.GwtCompatible;
import com.google.common.base.Preconditions;

/**
 * Implementation of {@link ImmutableSet} with exactly one element.
 *
 * @author Kevin Bourrillion
 * @author Nick Kralevich
 */
@GwtCompatible(serializable = true)
@SuppressWarnings("serial") // uses writeReplace(), not default serialization
final class SingletonImmutableSet<E> extends ImmutableSet<E> {
  final transient E element;

  // Non-volatile because:
  //   - Integer is immutable and thus thread-safe;
  //   - no problems if one thread overwrites the cachedHashCode from another.
  private transient Integer cachedHashCode;

  SingletonImmutableSet(E element) {
    this.element = Preconditions.checkNotNull(element);
  }

  @Pure SingletonImmutableSet(E element, int hashCode) {
    // Guaranteed to be non-null by the presence of the pre-computed hash code.
    this.element = element;
    cachedHashCode = hashCode;
  }

  @Override
@Pure public int size() {
    return 1;
  }

  @Pure @Override public boolean isEmpty() {
    return false;
  }

  @Pure @Override public boolean contains(/*@Nullable*/ Object target) {
    return element.equals(target);
  }

  @Override public UnmodifiableIterator<E> iterator() {
    return Iterators.singletonIterator(element);
  }

  @Override public Object[] toArray() {
    return new Object[] { element };
  }

  @SuppressWarnings({"unchecked","nullness"})
  @Override public <T extends /*@Nullable*/ Object> /*@Nullable*/ T[] toArray(T[] array) {
    if (array.length == 0) {
      array = ObjectArrays.newArray(array, 1);
    } else if (array.length > 1) {
      array[1] = null;
    }
    // Writes will produce ArrayStoreException when the toArray() doc requires.
    /*@Nullable*/ Object[] objectArray = array;
    objectArray[0] = element;
    return array;
  }

  @Pure @Override public boolean equals(@Nullable Object object) {
    if (object == this) {
      return true;
    }
    if (object instanceof Set) {
      Set<?> that = (Set<?>) object;
      return that.size() == 1 && element.equals(that.iterator().next());
    }
    return false;
  }

  @Pure @Override public final int hashCode() {
    Integer code = cachedHashCode;
    if (code == null) {
      return cachedHashCode = element.hashCode();
    }
    return code;
  }

  @Pure @Override boolean isHashCodeFast() {
    return false;
  }

  @Pure @Override public String toString() {
    String elementToString = element.toString();
    return new StringBuilder(elementToString.length() + 2)
        .append('[')
        .append(elementToString)
        .append(']')
        .toString();
  }
}
